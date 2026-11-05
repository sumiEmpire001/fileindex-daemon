"""Index local file metadata and search a snapshot."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    checksum=hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda:file.read(65536),b""):
            checksum.update(block)
    return checksum.hexdigest()


def index(root,hash_files=False):
    base=Path(root).resolve()
    if not base.is_dir():
        raise ValueError("root must be a directory")
    items=[]
    for path in sorted(base.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            stat=path.stat()
            item={"path":path.relative_to(base).as_posix(),"size":stat.st_size,"modified_ns":stat.st_mtime_ns}
            if hash_files:
                item["sha256"]=digest(path)
            items.append(item)
        except OSError:
            continue
    return {"root":str(base),"files":items,"count":len(items)}


def search(snapshot,query="",extension="",min_size=0):
    if not isinstance(snapshot,dict) or not isinstance(snapshot.get("files"),list):
        raise ValueError("invalid snapshot")
    return [item for item in snapshot["files"] if query.casefold() in item["path"].casefold()
            and (not extension or item["path"].lower().endswith(extension.lower()))
            and item["size"]>=min_size]


def compare(before,after):
    old={item["path"]:item for item in before["files"]}
    new={item["path"]:item for item in after["files"]}
    return {"added":sorted(new.keys()-old.keys()),"removed":sorted(old.keys()-new.keys()),
            "changed":sorted(path for path in old.keys()&new.keys()
                             if any(old[path].get(key)!=new[path].get(key) for key in ("size","modified_ns","sha256")))}


def main():
    parser=argparse.ArgumentParser(description="Local file metadata index")
    sub=parser.add_subparsers(dest="command",required=True)
    build=sub.add_parser("build")
    build.add_argument("directory")
    build.add_argument("--output",required=True)
    build.add_argument("--hash",action="store_true")
    query=sub.add_parser("search")
    query.add_argument("snapshot")
    query.add_argument("--query",default="")
    query.add_argument("--extension",default="")
    query.add_argument("--min-size",type=int,default=0)
    args=parser.parse_args()
    if args.command=="build":
        result=index(args.directory,args.hash)
        Path(args.output).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
        print(f"Indexed {result['count']} files")
    else:
        snapshot=json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
        print(json.dumps(search(snapshot,args.query,args.extension,args.min_size),indent=2))


if __name__=="__main__":
    main()
