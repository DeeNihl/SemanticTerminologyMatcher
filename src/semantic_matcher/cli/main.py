"""CLI commands for Semantic Terminology Matcher."""

import logging
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.progress import track

from ..core.csv_loader import CSVLoader
from ..core.vector_store import VectorStore
from ..config import settings

# Initialize console for rich output
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Semantic Terminology Matcher - OMOP Concepts Vector Store CLI."""
    pass


@cli.command()
@click.argument("csv_path", type=click.Path(exists=True))
@click.option(
    "--recreate",
    is_flag=True,
    help="Recreate the collection before uploading",
)
@click.option(
    "--batch-size",
    default=100,
    help="Batch size for uploading",
)
def upload(csv_path: str, recreate: bool, batch_size: int):
    """
    Upload OMOP concepts from a CSV file to the vector store.

    CSV_PATH: Path to the CSV file containing OMOP concepts
    """
    console.print(f"[bold blue]Loading CSV from:[/bold blue] {csv_path}")

    try:
        # Initialize components
        loader = CSVLoader()
        vector_store = VectorStore()

        # Load concepts from CSV
        with console.status("[bold green]Loading concepts from CSV..."):
            concepts = loader.load_from_csv(csv_path)

        console.print(f"[green]✓[/green] Loaded {len(concepts)} concepts from CSV")

        if not concepts:
            console.print("[red]No valid concepts found in CSV[/red]")
            return

        # Recreate collection if requested
        if recreate:
            with console.status("[bold yellow]Recreating collection..."):
                vector_store.create_collection(recreate=True)
            console.print("[green]✓[/green] Collection recreated")
        else:
            # Ensure collection exists
            if not vector_store.collection_exists():
                with console.status("[bold yellow]Creating collection..."):
                    vector_store.create_collection()
                console.print("[green]✓[/green] Collection created")

        # Upload concepts
        console.print(f"[bold blue]Uploading {len(concepts)} concepts...[/bold blue]")
        uploaded_count = 0

        # Upload with progress bar
        for i in track(
            range(0, len(concepts), batch_size),
            description="Uploading batches...",
        ):
            batch = concepts[i : i + batch_size]
            count = vector_store.upload_concepts(batch, batch_size=len(batch))
            uploaded_count += count

        console.print(
            f"[bold green]✓ Successfully uploaded {uploaded_count} concepts[/bold green]"
        )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.argument("query")
@click.option(
    "--limit",
    default=10,
    help="Maximum number of results to return",
)
@click.option(
    "--score-threshold",
    type=float,
    default=None,
    help="Minimum similarity score (0-1)",
)
def search(query: str, limit: int, score_threshold: float):
    """
    Search for OMOP concepts using semantic similarity.

    QUERY: The search query text
    """
    console.print(f"[bold blue]Searching for:[/bold blue] '{query}'")

    try:
        vector_store = VectorStore()

        if not vector_store.collection_exists():
            console.print(
                "[red]Collection does not exist. Please upload data first.[/red]"
            )
            return

        # Perform search
        with console.status("[bold green]Searching..."):
            results = vector_store.search(
                query=query,
                limit=limit,
                score_threshold=score_threshold,
            )

        if not results:
            console.print("[yellow]No results found[/yellow]")
            return

        # Display results in a table
        table = Table(title=f"Search Results ({len(results)} found)")
        table.add_column("Concept ID", style="cyan", no_wrap=True)
        table.add_column("Concept Name", style="magenta")
        table.add_column("Score", style="green", justify="right")
        table.add_column("Definition", style="white")

        for result in results:
            # Truncate definition for display
            definition = (
                result.definition_chunk[:100] + "..."
                if len(result.definition_chunk) > 100
                else result.definition_chunk
            )
            table.add_row(
                str(result.concept_id),
                result.concept_name,
                f"{result.score:.4f}",
                definition,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.argument("concept_id", type=int)
def get(concept_id: int):
    """
    Retrieve a specific OMOP concept by ID.

    CONCEPT_ID: The concept ID to retrieve
    """
    try:
        vector_store = VectorStore()

        with console.status(f"[bold green]Retrieving concept {concept_id}..."):
            concept = vector_store.get_concept_by_id(concept_id)

        if concept is None:
            console.print(f"[red]Concept {concept_id} not found[/red]")
            return

        # Display concept details
        console.print(f"\n[bold cyan]Concept ID:[/bold cyan] {concept.concept_id}")
        console.print(f"[bold cyan]Name:[/bold cyan] {concept.concept_name}")
        console.print(f"[bold cyan]Domain:[/bold cyan] {concept.domain_id}")
        console.print(f"[bold cyan]Vocabulary:[/bold cyan] {concept.vocabulary_id}")
        console.print(f"[bold cyan]Class:[/bold cyan] {concept.concept_class_id}")
        console.print(f"[bold cyan]Code:[/bold cyan] {concept.concept_code}")
        console.print(f"\n[bold cyan]Definition:[/bold cyan]\n{concept.definition_chunk}")

        if concept.metadata_payload:
            console.print(f"\n[bold cyan]Metadata:[/bold cyan]")
            for key, value in concept.metadata_payload.items():
                console.print(f"  {key}: {value}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


@cli.command()
def info():
    """Display information about the vector store and collection."""
    try:
        vector_store = VectorStore()

        # Get health info
        health = vector_store.health_check()

        console.print("\n[bold cyan]Vector Store Information[/bold cyan]")
        console.print(f"[bold]Qdrant Host:[/bold] {settings.qdrant_host}")
        console.print(f"[bold]Qdrant Port:[/bold] {settings.qdrant_port}")
        console.print(f"[bold]Collection Name:[/bold] {settings.qdrant_collection_name}")
        console.print(f"[bold]Embedding Model:[/bold] {settings.embedding_model}")

        console.print(f"\n[bold cyan]Status[/bold cyan]")
        console.print(
            f"[bold]Connected:[/bold] {'✓ Yes' if health['connected'] else '✗ No'}"
        )
        console.print(
            f"[bold]Collection Exists:[/bold] {'✓ Yes' if health['collection_exists'] else '✗ No'}"
        )
        console.print(f"[bold]Total Points:[/bold] {health['total_points']}")

        if health["collection_exists"]:
            info = vector_store.get_collection_info()
            console.print(f"[bold]Vectors Count:[/bold] {info.get('vectors_count', 0)}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.option(
    "--recreate",
    is_flag=True,
    help="Recreate the collection if it exists",
)
def create_collection(recreate: bool):
    """Create the Qdrant collection."""
    try:
        vector_store = VectorStore()

        with console.status("[bold yellow]Creating collection..."):
            created = vector_store.create_collection(recreate=recreate)

        if created:
            console.print("[bold green]✓ Collection created successfully[/bold green]")
        else:
            console.print(
                "[yellow]Collection already exists. Use --recreate to recreate it.[/yellow]"
            )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.confirmation_option(prompt="Are you sure you want to delete the collection?")
def delete_collection():
    """Delete the Qdrant collection."""
    try:
        vector_store = VectorStore()

        with console.status("[bold red]Deleting collection..."):
            deleted = vector_store.delete_collection()

        if deleted:
            console.print("[bold green]✓ Collection deleted successfully[/bold green]")
        else:
            console.print("[yellow]Collection did not exist[/yellow]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.argument("csv_path", type=click.Path(exists=True))
def validate(csv_path: str):
    """
    Validate a CSV file without uploading.

    CSV_PATH: Path to the CSV file to validate
    """
    console.print(f"[bold blue]Validating CSV:[/bold blue] {csv_path}")

    try:
        loader = CSVLoader()

        with console.status("[bold green]Validating..."):
            result = loader.validate_csv(csv_path)

        if result["valid"]:
            console.print("[bold green]✓ CSV is valid[/bold green]")
            console.print(f"[bold]Total rows:[/bold] {result['total_rows']}")
            console.print(f"[bold]Columns:[/bold] {', '.join(result['columns'])}")

            # Show sample data
            if result.get("sample_data"):
                console.print("\n[bold cyan]Sample data (first 5 rows):[/bold cyan]")
                table = Table()

                # Add columns
                for col in result["columns"]:
                    table.add_column(col, style="cyan")

                # Add rows
                for row in result["sample_data"]:
                    table.add_row(*[str(row.get(col, "")) for col in result["columns"]])

                console.print(table)
        else:
            console.print(f"[bold red]✗ CSV is invalid:[/bold red] {result['error']}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


@cli.command()
@click.option(
    "--host",
    default=None,
    help=f"Host to bind to (default: {settings.api_host})",
)
@click.option(
    "--port",
    default=None,
    type=int,
    help=f"Port to bind to (default: {settings.api_port})",
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload for development",
)
def serve(host: str, port: int, reload: bool):
    """Start the FastAPI server."""
    import uvicorn

    host = host or settings.api_host
    port = port or settings.api_port

    console.print(f"[bold green]Starting server at http://{host}:{port}[/bold green]")
    console.print(f"[bold]API docs available at http://{host}:{port}/docs[/bold]")

    uvicorn.run(
        "semantic_matcher.api.app:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    cli()
