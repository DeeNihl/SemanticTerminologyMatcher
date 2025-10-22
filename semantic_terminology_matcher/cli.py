"""
Command-line interface for Semantic Terminology Matcher
"""
import click
import sys
from pathlib import Path
from typing import Optional

from .csv_loader import CSVLoader
from .vector_store import VectorStore
from .config import settings


@click.group()
@click.version_option()
def main():
    """Semantic Terminology Matcher - Load and search terminology using vector embeddings"""
    pass


@main.command()
@click.argument("csv_file", type=click.Path(exists=True))
@click.option(
    "--collection",
    default=settings.qdrant_collection,
    help="Qdrant collection name",
)
@click.option(
    "--recreate",
    is_flag=True,
    help="Recreate collection if it exists",
)
@click.option(
    "--host",
    default=settings.qdrant_host,
    help="Qdrant host",
)
@click.option(
    "--port",
    default=settings.qdrant_port,
    help="Qdrant port",
)
@click.option(
    "--memory",
    is_flag=True,
    default=settings.qdrant_use_memory,
    help="Use in-memory storage",
)
def load(
    csv_file: str,
    collection: str,
    recreate: bool,
    host: str,
    port: int,
    memory: bool,
):
    """Load terminology from CSV file into Qdrant vector store"""
    try:
        click.echo(f"Loading terminology from {csv_file}...")
        
        # Load CSV
        loader = CSVLoader()
        entries = loader.load_from_csv(csv_file)
        click.echo(f"Loaded {len(entries)} entries from CSV")
        
        # Initialize vector store
        click.echo(f"Connecting to Qdrant (host={host}, port={port}, memory={memory})...")
        vector_store = VectorStore(
            host=host,
            port=port,
            collection_name=collection,
            use_memory=memory,
        )
        
        # Create collection
        click.echo(f"Creating collection '{collection}'...")
        vector_store.create_collection(recreate=recreate)
        
        # Add entries
        click.echo("Adding entries to vector store...")
        count = vector_store.add_entries(entries)
        click.echo(f"Successfully added {count} entries to vector store")
        
        # Show stats
        stats = vector_store.get_stats()
        click.echo(f"Collection stats: {stats}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("query")
@click.option(
    "--limit",
    default=10,
    type=int,
    help="Maximum number of results",
)
@click.option(
    "--threshold",
    type=float,
    help="Minimum similarity score (0-1)",
)
@click.option(
    "--category",
    help="Filter by category",
)
@click.option(
    "--collection",
    default=settings.qdrant_collection,
    help="Qdrant collection name",
)
@click.option(
    "--host",
    default=settings.qdrant_host,
    help="Qdrant host",
)
@click.option(
    "--port",
    default=settings.qdrant_port,
    help="Qdrant port",
)
@click.option(
    "--memory",
    is_flag=True,
    default=settings.qdrant_use_memory,
    help="Use in-memory storage",
)
def search(
    query: str,
    limit: int,
    threshold: Optional[float],
    category: Optional[str],
    collection: str,
    host: str,
    port: int,
    memory: bool,
):
    """Search for terminology entries"""
    try:
        click.echo(f"Searching for: {query}")
        
        # Initialize vector store
        vector_store = VectorStore(
            host=host,
            port=port,
            collection_name=collection,
            use_memory=memory,
        )
        
        # Search
        results = vector_store.search(
            query=query,
            limit=limit,
            score_threshold=threshold,
            category_filter=category,
        )
        
        # Display results
        if not results:
            click.echo("No results found")
            return
        
        click.echo(f"\nFound {len(results)} results:\n")
        for i, result in enumerate(results, 1):
            click.echo(f"{i}. {result.entry.term} (Code: {result.entry.code})")
            click.echo(f"   Score: {result.score:.4f}")
            if result.entry.description:
                click.echo(f"   Description: {result.entry.description}")
            if result.entry.category:
                click.echo(f"   Category: {result.entry.category}")
            click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--collection",
    default=settings.qdrant_collection,
    help="Qdrant collection name",
)
@click.option(
    "--host",
    default=settings.qdrant_host,
    help="Qdrant host",
)
@click.option(
    "--port",
    default=settings.qdrant_port,
    help="Qdrant port",
)
@click.option(
    "--memory",
    is_flag=True,
    default=settings.qdrant_use_memory,
    help="Use in-memory storage",
)
def stats(
    collection: str,
    host: str,
    port: int,
    memory: bool,
):
    """Show collection statistics"""
    try:
        # Initialize vector store
        vector_store = VectorStore(
            host=host,
            port=port,
            collection_name=collection,
            use_memory=memory,
        )
        
        # Get stats
        stats = vector_store.get_stats()
        
        click.echo(f"Collection: {collection}")
        if stats.get("exists"):
            click.echo(f"Vectors count: {stats.get('vectors_count', 0)}")
            click.echo(f"Points count: {stats.get('points_count', 0)}")
        else:
            click.echo("Collection does not exist")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
