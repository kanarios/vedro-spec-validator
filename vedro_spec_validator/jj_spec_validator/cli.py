import time
from typing import List

import click

from ._config import Config
from .spec import Spec
from .utils._cacheir import save_cache


@click.command()
@click.argument('spec_links', nargs=-1, required=True)
@click.option('--timeout', default=Config.GET_SPEC_TIMEOUT, help='Timeout for downloading specs in seconds')
@click.option('--cache-processed',
              default=Config.CACHE_AS_PROCESSED_SCHEMAS,
              help='Convert specifications into schemas and cache them that way')
def cache_specs(spec_links: List[str], timeout: int, cache_processed: bool) -> None:
    """
    Pre-downloads and caches specifications from provided URLs.
    
    SPEC_LINKS: One or more specification URLs to cache
    """
    start_time = time.time()
    click.echo(f"Starting caching of {len(spec_links)} specifications...")

    for spec_link in spec_links:
        spec_start_time = time.time()
        try:
            click.echo(f"\nProcessing {spec_link}...")
            spec = Spec(spec_link=spec_link, func_name="cache_specs")
            response = spec._download_spec()

            if response is None:
                click.echo(f"❌ Failed to download specification: {spec_link}")
                continue

            raw_spec = spec._parse_spec(response)
            if cache_processed:
                click.echo("Processing specification before caching...")
                schema_data = spec._get_schema_from_json(raw_spec)
                dict_of_schemas = spec._build_dict_of_schemas(schema_data)
                save_cache(spec_link=spec_link, obj=dict_of_schemas)
            else:
                save_cache(spec_link=spec_link, obj=raw_spec)
            spec_time = time.time() - spec_start_time
            click.echo(f"✅ Specification successfully cached: {spec_link} (took {spec_time:.2f}s)")

        except Exception as e:
            spec_time = time.time() - spec_start_time
            click.echo(f"❌ Error processing {spec_link}: {str(e)} (took {spec_time:.2f}s)")

    total_time = time.time() - start_time
    click.echo(f"\nCaching completed! Total time: {total_time:.2f}s")


if __name__ == '__main__':
    cache_specs()
