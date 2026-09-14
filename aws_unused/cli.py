import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import typer

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from aws_unused import __version__
from aws_unused.collectors import COLLECTORS, SUPPORTED_SERVICES
from aws_unused.utils.aws_session import AWSSession
from aws_unused.analyzer.findings import FindingsAnalyzer
from aws_unused.exporter.excel import ExcelExporter


console = Console()

app = typer.Typer(
    name="aws-unused",
    help="Read-only AWS unused resource scanner."
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version."
    )
):
    if version:
        typer.echo(__version__)
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@app.command()
def scan(
    service: str = typer.Option(
    None,
    "--service",
    "-s",
    help=(
        "Scan a single service. "
        f"Available: {', '.join(SUPPORTED_SERVICES)}"
    ),
    case_sensitive=False
    ),
    output: str = typer.Option(
        "unused_resources.xlsx",
        "--output",
        "-o",
        help="Excel report filename."
    ),
    region: str = typer.Option(
        None,
        "--region",
        help="AWS region."
    ),
    profile: str = typer.Option(
        None,
        "--profile",
        help="AWS CLI profile name."
    ),
    workers: int = typer.Option(
        6,
        "--workers",
        "-w",
        help="Maximum parallel collectors."
    )
):
    if service and service.lower() not in SUPPORTED_SERVICES:
        console.print(
            f"[red]Invalid service:[/red] {service}"
        )
        console.print(
            f"Supported services: {', '.join(SUPPORTED_SERVICES)}"
        )
        raise typer.Exit(code=1)

    if workers < 1:
        typer.echo("Workers must be at least 1.")
        raise typer.Exit(code=1)

    service = service.lower() if service else None

    aws = AWSSession(
        region=region,
        profile=profile
    )

    console.print(
    Panel(
        "[bold]AWS Unused Resources Finder[/bold]\n"
        "Read-only AWS resource scanner",
        expand=False
    )
    )

    console.print(f"[bold]AWS Account:[/bold] {aws.account_id()}")
    console.print(f"[bold]AWS Region:[/bold]  {aws.region}")
    console.print()

    selected = (
        {service: COLLECTORS[service]}
        if service
        else COLLECTORS
    )

    findings = []
    start = time.time()

    with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    console=console
) as progress:

        task = progress.add_task(
            "Scanning AWS resources...",
            total=len(selected)
        )

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(collector(aws).collect): collector
                for collector in selected.values()
            }

            for future in as_completed(futures):
                collector = futures[future]

                try:
                    result = future.result()
                    findings.extend(result)

                    progress.update(
                        task,
                        advance=1,
                        description=(
                            f"[green]✓[/green] "
                            f"{collector.display_name}: "
                            f"{len(result)} findings"
                        )
                    )

                except Exception as e:
                    progress.update(
                        task,
                        advance=1,
                        description=(
                            f"[red]✗[/red] "
                            f"{collector.display_name}: "
                            f"{e}"
                        )
                    )

    duration = round(time.time() - start, 2)

    analyzer = FindingsAnalyzer(findings)
    summary = analyzer.summary()

    exporter = ExcelExporter(
        findings=findings,
        aws=aws,
        output=output
    )

    exporter.export()

    table = Table(title="Scan Summary")

    table.add_column("Metric")
    table.add_column("Value")

    table.add_row("Total Findings", str(summary["total"]))
    table.add_row("Output File", output)
    table.add_row("Duration", f"{duration}s")

    console.print(table)


if __name__ == "__main__":
    app()