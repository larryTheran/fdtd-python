#!/usr/bin/env python3
"""Package existing simulation outputs without rerunning or modifying them.

Run from the repository root, with results/ and results_3d/ restored or generated:
    python scripts/pack_results.py --source . --assets ../release-assets/fdtd-python

ZIP members preserve results/... and results_3d/... paths. Only OS/cache files
are excluded. Existing output packages are refused unless --replace is given.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

EXCLUDED_PARTS = {'.DS_Store', '__pycache__', '.pytest_cache', '.cache'}
TEXT_SUFFIXES = {'.json', '.txt', '.md', '.log', '.xml', '.html', '.csv'}
SECRET_PATTERNS = {
    'private_key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    'github_token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b'),
    'aws_access_key': re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'credential_url': re.compile(r'https?://[^\s/:]+:[^\s/@]+@'),
    'secret_assignment': re.compile(r'(?im)^\s*["\']?(?:password|passwd|api[_-]?key|access[_-]?token|client[_-]?secret)["\']?\s*[:=]\s*["\'][^"\'\s]{6,}["\']'),
}


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        while chunk := stream.read(4 * 1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def files_under(directory: Path):
    for path in sorted(directory.rglob('*')):
        if path.is_file() and not any(part in EXCLUDED_PARTS for part in path.relative_to(directory).parts):
            if path.is_symlink():
                raise ValueError(f'Result symlinks require manual review: {path.name}')
            yield path


def parse_config(directory: Path) -> dict:
    path = directory / 'config.json'
    return json.loads(path.read_text()) if path.is_file() else {}


def dimension(config: dict, root_name: str) -> str:
    if 'nz' in config or root_name == 'results_3d':
        return '3d'
    if 'cells' in config:
        return '1d'
    if 'nx' in config and 'ny' in config:
        return '2d'
    raise ValueError('Cannot classify experiment from config')


def inventory(source: Path):
    experiments = []
    support = []
    for root_name in ('results', 'results_3d'):
        root = source / root_name
        if not root.is_dir():
            raise ValueError(f'Missing result folder: {root_name}')
        for child in sorted(root.iterdir()):
            if child.name in EXCLUDED_PARTS:
                continue
            if child.is_dir():
                contents = list(files_under(child))
                config = parse_config(child)
                experiments.append(dict(name=child.name, dimension=dimension(config, root_name),
                    directory=child, files=contents, config=config,
                    size_bytes=sum(path.stat().st_size for path in contents)))
            elif child.is_file():
                support.append(child)
    return experiments, support


def archive_plan(experiments, support, target_bytes):
    plans = []
    for dim in ('1d', '2d'):
        group = [item for item in experiments if item['dimension'] == dim]
        plans.append(dict(name=f'fdtd-results-{dim}.zip', dimension=dim,
            experiments=group, files=[path for item in group for path in item['files']]))
    chunks = []
    current = []
    size = 0
    for item in (entry for entry in experiments if entry['dimension'] == '3d'):
        if current and size + item['size_bytes'] > target_bytes:
            chunks.append(current); current = []; size = 0
        current.append(item); size += item['size_bytes']
    if current:
        chunks.append(current)
    for number, group in enumerate(chunks, 1):
        plans.append(dict(name=f'fdtd-results-3d-part-{number:02d}.zip', dimension='3d',
            experiments=group, files=[path for item in group for path in item['files']]))
    if support:
        plans.append(dict(name='fdtd-results-support.zip', dimension='support', experiments=[], files=support))
    return plans


def scan_text(path, relative):
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return []
    text = path.read_text(encoding='utf-8', errors='replace')
    return [{'path': relative, 'pattern': name, 'matches': len(pattern.findall(text))}
        for name, pattern in SECRET_PATTERNS.items() if pattern.search(text)]


def script_for(source, item):
    name = item['name'] + '.py'
    candidates = [source/'experiments_3d'/name] if item['dimension'] == '3d' else [source/'experiments'/folder/name for folder in ('one_d', 'two_d', 'supplemental')]
    return next((p.relative_to(source).as_posix() for p in candidates if p.is_file()), None)


def create_packages(source, assets, catalog, repository, tag, target_bytes, replace):
    source = source.resolve(); assets = assets.resolve(); catalog = catalog.resolve()
    if source == assets or source in assets.parents:
        raise ValueError('Assets must be outside the source tree')
    experiments, support = inventory(source)
    plans = archive_plan(experiments, support, target_bytes)
    assets.mkdir(parents=True, exist_ok=True)
    catalog.mkdir(parents=True, exist_ok=True)
    destinations = [assets/plan['name'] for plan in plans]
    existing = [p.name for p in destinations if p.exists()]
    if existing and not replace:
        raise ValueError('Archives already exist; use --replace: ' + ', '.join(existing))
    records = []; findings = []; archive_summaries = []; experiment_records = []
    base = f'https://github.com/{repository}/releases/download/{tag}'
    source_files = {p.relative_to(source).as_posix() for root in ('results', 'results_3d') for p in files_under(source/root)}
    seen = set()
    for plan in plans:
        destination = assets/plan['name']
        partial = destination.with_suffix('.zip.partial')
        plan_records = []
        with zipfile.ZipFile(partial, 'w', compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
            for path in sorted(plan['files']):
                relative = path.relative_to(source).as_posix()
                if relative in seen:
                    raise ValueError('Duplicate archive member: '+relative)
                seen.add(relative)
                before = path.stat()
                checksum = digest_file(path)
                record = dict(path=relative, size_bytes=before.st_size, sha256=checksum,
                    dimension=plan['dimension'], archive=plan['name'], download_url=f'{base}/{plan["name"]}')
                records.append(record); plan_records.append(record)
                findings.extend(scan_text(path, relative))
                archive.write(path, relative)
                after = path.stat()
                if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                    raise ValueError('Source changed while packaging: '+relative)
        partial.replace(destination)
        if destination.stat().st_size >= 2 * 1024**3:
            raise ValueError('Archive exceeds GitHub asset limit: '+destination.name)
        # Read back every complete archive member and verify both ZIP CRC and
        # SHA256 against its original file record. No extraction is necessary.
        with zipfile.ZipFile(destination) as archive:
            assert set(archive.namelist()) == {record['path'] for record in plan_records}
            for record in plan_records:
                h = hashlib.sha256()
                with archive.open(record['path']) as stream:
                    while chunk := stream.read(4 * 1024 * 1024): h.update(chunk)
                if h.hexdigest() != record['sha256']:
                    raise ValueError('Archive content mismatch: '+record['path'])
        archive_summaries.append(dict(name=plan['name'], dimension=plan['dimension'],
            size_bytes=destination.stat().st_size, sha256=digest_file(destination),
            files=len(plan_records), experiments=[item['name'] for item in plan['experiments']],
            download_url=f'{base}/{plan["name"]}'))
        record_by_path = {record['path']: record for record in plan_records}
        for item in plan['experiments']:
            prefix = item['directory'].relative_to(source).as_posix()
            preview_dir = catalog/'previews'/item['dimension']/item['name']
            metadata_dir = catalog/'metadata'/item['dimension']/item['name']
            previews = []; metadata = []
            for path in item['files']:
                if path.suffix.lower() == '.png':
                    target=preview_dir/path.name; target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(path,target)
                    if digest_file(target) != record_by_path[path.relative_to(source).as_posix()]['sha256']:
                        raise ValueError('Preview copy mismatch: '+path.name)
                    previews.append(target.relative_to(catalog).as_posix())
                elif path.suffix.lower() == '.json':
                    target=metadata_dir/path.name; target.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(path,target)
                    if digest_file(target) != record_by_path[path.relative_to(source).as_posix()]['sha256']:
                        raise ValueError('Metadata copy mismatch: '+path.name)
                    metadata.append(target.relative_to(catalog).as_posix())
            config = item['config']
            experiment_records.append(dict(name=item['name'],dimension=item['dimension'],title=config.get('title',item['name']),
                source_script=script_for(source,item),original_directory=prefix,
                size_bytes=item['size_bytes'],files=len(item['files']),
                output_types=dict(Counter(p.suffix.lower() for p in item['files'])),
                archive=plan['name'],download_url=f'{base}/{plan["name"]}',previews=previews,metadata=metadata,
                steps=config.get('steps'),grid=[config['cells']] if 'cells' in config else [config.get(k) for k in ('nx','ny','nz') if config.get(k) is not None],
                thesis_reference=config.get('thesis'),notes=config.get('notes','')))
        print(f'Verified {plan["name"]}: {len(plan_records)} files, {destination.stat().st_size:,} bytes',flush=True)
    if seen != source_files:
        raise ValueError(f'Incomplete coverage: missing={len(source_files-seen)}, extra={len(seen-source_files)}')
    records.sort(key=lambda r:r['path']); experiment_records.sort(key=lambda r:(r['dimension'],r['name']))
    manifest = dict(schema_version=1,repository=repository,release_tag=tag,
        snapshot_date=tag.removeprefix('results-') if re.fullmatch(r'results-\d{4}-\d{2}-\d{2}',tag) else None,
        scope='All files in results/ and results_3d/, excluding .DS_Store and cache directories',
        total_files=len(records),total_bytes=sum(r['size_bytes'] for r in records),
        files=records)
    (catalog/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    with (catalog/'manifest.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['path','size_bytes','sha256','dimension','archive','download_url']);writer.writeheader();writer.writerows(records)
    (catalog/'experiments.json').write_text(json.dumps(experiment_records,indent=2,ensure_ascii=False)+'\n')
    summary=dict(repository=repository,release_tag=tag,total_files=manifest['total_files'],total_bytes=manifest['total_bytes'],
        experiments_by_dimension=dict(Counter(r['dimension'] for r in experiment_records)),
        archives=archive_summaries,verification='Every ZIP member SHA256 matches its source file record; complete source-file coverage verified',
        secret_scan_findings=findings)
    (catalog/'archives.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    (assets/'results-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    (assets/'results-experiments.json').write_text(json.dumps(experiment_records,indent=2,ensure_ascii=False)+'\n')
    (assets/'results-archives.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    (assets/'SHA256SUMS').write_text(''.join(f'{digest_file(path)}  {path.name}\n' for path in sorted(assets.iterdir()) if path.is_file() and path.name!='SHA256SUMS'))
    lines=['# Complete simulation results','',f'Snapshot: **{tag}** · {len(experiment_records)} experiments · {len(records)} files · {manifest["total_bytes"]:,} uncompressed bytes.','',
        'Every saved result file is included in the release ZIPs. The repository contains all static PNG previews and small JSON configurations/diagnostics for browsing. Numerical NPZ arrays, GIF animations, logs and original indexes are preserved in the downloadable archives.','',
        'Download the archives you need from [the result release](https://github.com/'+repository+'/releases/tag/'+tag+'). Extract at the repository root: ZIP members recreate the original `results/` and `results_3d/` folders. No recomputation is required.','',
        'Per-file SHA256 hashes are in [manifest.json](manifest.json) and [manifest.csv](manifest.csv); [archives.json](archives.json) lists ZIP sizes and hashes. [experiments.json](experiments.json) provides machine-readable configuration/provenance pointers.','',
        '## Download archives','','| Archive | Scope | Files | Size |','| --- | --- | ---: | ---: |']
    for archive in archive_summaries:
        lines.append(f'| [{archive["name"]}]({archive["download_url"]}) | {archive["dimension"].upper()} | {archive["files"]} | {archive["size_bytes"]/1024**2:.1f} MiB |')
    lines+=['','## Browse experiments','', 'The stored figures are prior computed results, not promises of convergence or physical equivalence. Read the numerical limitations and source-reference notes before interpreting them.','']
    for dim in ('1d','2d','3d'):
        lines+=['### '+dim.upper(),'','| Experiment | Grid / steps | Saved previews | Configuration / diagnostics | Download |','| --- | --- | --- | --- | --- |']
        for item in (r for r in experiment_records if r['dimension']==dim):
            preview_links=' · '.join(f'[{Path(p).stem}]({p})' for p in item['previews'])
            meta_links=' · '.join(f'[{Path(p).stem}]({p})' for p in item['metadata'])
            title=f'[{item["name"]}](../{item["source_script"]})' if item['source_script'] else item['name']
            grid='×'.join(map(str,item['grid']))
            lines.append(f'| {title} | {grid} / {item["steps"]:,} | {preview_links} | {meta_links} | [ZIP]({item["download_url"]}) |')
        lines.append('')
    lines+=['## Rebuild and verify packages','', '```bash','python scripts/pack_results.py --source . --assets ../release-assets/fdtd-python \\',f'  --repository {repository} --tag {tag}','```','',
        'This packages existing outputs only. It does not run simulations or change result files. It refuses to overwrite archive ZIPs unless `--replace` is explicit. Generated archives use stored ZIP entries because NPZ, PNG and GIF data are already compressed. Every member is read back and verified before the manifest is accepted.','']
    (catalog/'README.md').write_text('\n'.join(lines))
    print(json.dumps({k:summary[k] for k in ('total_files','total_bytes','experiments_by_dimension','verification','secret_scan_findings')},indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=Path('.'),help='Project containing results/ and results_3d/')
    parser.add_argument('--assets',type=Path,required=True,help='Output folder outside source tree')
    parser.add_argument('--catalog',type=Path,default=Path('results-catalog'))
    parser.add_argument('--repository',default='larryTheran/fdtd-python')
    parser.add_argument('--tag',default='results-2026-11-04')
    parser.add_argument('--target-mib',type=int,default=900)
    parser.add_argument('--replace',action='store_true')
    args=parser.parse_args()
    if not 1 <= args.target_mib < 1900:
        parser.error('--target-mib must be between 1 and 1899')
    create_packages(args.source,args.assets,args.catalog,args.repository,args.tag,args.target_mib*1024**2,args.replace)

if __name__=='__main__':main()
