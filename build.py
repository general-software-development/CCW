from rich.progress import Progress
from rich.console import Console
import importlib.util
import asyncio as aio
import argparse
import pathlib
from threading import Lock
from dataclasses import dataclass

class ValidationError(Exception):
    ...

@dataclass
class CCWData:
    title: str
    identifier: str | int
    description: str | None | tuple[str]
    _path: str

    def validate(self):
        if not isinstance(self.identifier, (str, int)):
            raise ValidationError("CCW Identifier is not a string or an integer.")
        if not isinstance(self.title, str):
            raise ValidationError(f"CCW Title for {self.identifier} is not a string.")
        if (not isinstance(self.description, (str, tuple))) and self.description is not None:
            raise ValidationError("CCW Description is not a string or NoneType.")

async def main():
    parser = argparse.ArgumentParser("Build")
    parser.add_argument("path")

    args = parser.parse_args()
    path = pathlib.Path(args.path)
    data_lock = Lock()
    ccw_list: list[CCWData] = []

    asyncs = []

    with Progress() as p:
        task = p.add_task("Processing CCW entries (#null)", total=len(list((path / "ccw").rglob("*.py"))))

        for file in (path / "ccw").rglob("*.py"):
            def handle(file: pathlib.Path):
                spec = importlib.util.spec_from_file_location(f"ccw_{file.stem}", file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                identifier = module.identifier()
                data = CCWData(title = module.title(), identifier = identifier, description = module.description() if hasattr(module, "description") else None, _path = file.relative_to(path / "ccw"))
                with data_lock:
                    ccw_list.append(data)
                    p.advance(task)
                    p.update(task, description=f"Processing CCW entries (#{identifier})")

            asyncs.append(aio.create_task(aio.to_thread(handle, file)))

        await aio.gather(*asyncs)

    with Progress() as p:
        task = p.add_task("Emitting markdown files", total=len(ccw_list) + 1)
        dist = path.parent / "docs"
        dist.mkdir(0o771, exist_ok=True)

        total_bytes: int = 0

        def sort(l: list, k = None, reverse: bool = False) -> list:
            l2 = l.copy()
            l2.sort(key = k, reverse=reverse)
            return l2

        index_markdown_content = (
            "# Community Common Weaknesses Index (CCW Index)\r\n\n"
            "* **CCW 0xx**\r\n"
            + '\r\n'.join(
                [
                    f"  * [CCW-{str(ccw.identifier).rjust(3, '0')}]({f'ccw_{ccw.identifier}.md'})"
                    for ccw in sort(list(filter(lambda ccw: ccw.identifier < 100, ccw_list)), lambda ccw: ccw.identifier)
                ]
            )
        )
        with open(dist / "index.md", "w", newline="\n") as f:
            f.write(index_markdown_content)
            total_bytes += len(index_markdown_content.encode("utf-8"))
            p.advance(task)

        for ccw in ccw_list:
            content = "---\n"
            content += f"title: CCW-{str(ccw.identifier).rjust(3, '0')} \"{ccw.title}\"\n"
            content += "---\n"
            content += "\n"
            content += f"{ccw.description if isinstance(ccw.description, str) else '\t' + '\r\n\n\t'.join(ccw.description) if ccw.description is not None else ""}".replace("\t", "&emsp;")

            with open(dist / f"ccw_{ccw.identifier}.md", "w", newline="\n") as f:
                f.write(content)
                p.advance(task)

if __name__ == "__main__":
    aio.run(main())
