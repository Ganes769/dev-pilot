import os
from typing import List

import requests
import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

app = typer.Typer()
console = Console()

BASE_URL = os.environ.get("DEVPILOT_URL", "http://127.0.0.1:8000")


@app.command()
def index(
    repo_path: str,
    chunk_size: int = 1000,
    overlap: int = 100,
):
    """
    Index a repository into DevPilot.
    """
    payload = {
        "repo_path": repo_path,
        "chunk_size": chunk_size,
        "overlap": overlap,
    }

    try:
        with console.status(
            "[bold cyan]Scanning repo, chunking, embedding, upserting to vector store…[/bold cyan]",
            spinner="dots12",
        ):
            response = requests.post(
                f"{BASE_URL}/repos/embed", json=payload, timeout=600
            )
        response.raise_for_status()
        data = response.json()

        stats = Table.grid(padding=(0, 2))
        stats.add_column(style="dim cyan", justify="right")
        stats.add_column(style="white")
        stats.add_row("Repo", data["repo_name"])
        stats.add_row("Files", str(data["total_files"]))
        stats.add_row("Chunks", str(data["total_chunks"]))
        stats.add_row("Vectors", str(data["vectors_stored"]))
        stats.add_row("Collection", data["collection"])

        console.print()
        console.print(
            Panel(
                stats,
                title="[bold green]Indexed[/bold green]",
                subtitle="DevPilot",
                border_style="green",
                padding=(1, 2),
            )
        )

    except requests.exceptions.RequestException as e:
        console.print(
            Panel(
                f"[bold red]Indexing failed[/bold red]\n\n{e}",
                border_style="red",
            )
        )


@app.command()
def ask(
    question: List[str] = typer.Argument(
        ...,
        help="Question about the indexed repo (all words after 'ask' are joined).",
    ),
    limit: int = 3,
):
    """
    Ask DevPilot a question about the indexed repository.

    Example: python cli.py ask what does the embed endpoint do
    """
    q = " ".join(question).strip()
    if not q:
        console.print(
            Panel("[bold red]Empty question.[/bold red]", border_style="red")
        )
        raise typer.Exit(code=1)

    payload = {"question": q, "limit": limit}

    try:
        with console.status(
            "[bold cyan]Searching codebase and generating answer…[/bold cyan]",
            spinner="dots12",
        ):
            response = requests.post(f"{BASE_URL}/ask", json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()

        console.print()
        console.print(Rule("[bold white]DevPilot[/bold white]", style="bright_blue"))
        console.print(
            Panel(
                data["question"],
                title="[bold cyan]Question[/bold cyan]",
                border_style="cyan",
                padding=(1, 2),
            )
        )
        console.print(
            Panel(
                Markdown(data.get("answer") or "_No answer._"),
                title="[bold green]Answer[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )

        sources = data.get("sources") or []
        if sources:
            table = Table(
                title="[bold magenta]Sources[/bold magenta]",
                show_header=True,
                header_style="bold",
                border_style="magenta",
                expand=True,
            )
            table.add_column("#", style="dim", width=3, justify="right")
            table.add_column("File", style="cyan", no_wrap=True, ratio=2)
            table.add_column("Chunk", justify="right", style="yellow")
            table.add_column("Score", justify="right", style="green")
            for i, source in enumerate(sources, start=1):
                table.add_row(
                    str(i),
                    source.get("file_path", ""),
                    str(source.get("chunk_index", "")),
                    f"{source.get('score', 0):.4f}",
                )
            console.print(table)
        else:
            console.print(
                Panel(
                    "[dim]No retrieval hits above the similarity threshold.[/dim]",
                    title="[yellow]Sources[/yellow]",
                    border_style="yellow",
                )
            )

    except requests.exceptions.HTTPError as e:
        detail = ""
        if e.response is not None:
            try:
                body = e.response.json()
                detail = body.get("detail", str(body))
            except Exception:
                detail = e.response.text or str(e)
        console.print(
            Panel(
                f"[bold red]Ask failed[/bold red]\n\n{detail or e}",
                border_style="red",
            )
        )
        raise typer.Exit(code=1)
    except requests.exceptions.RequestException as e:
        console.print(
            Panel(f"[bold red]Ask failed[/bold red]\n\n{e}", border_style="red")
        )
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()