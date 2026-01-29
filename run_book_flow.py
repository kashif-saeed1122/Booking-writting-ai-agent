import argparse
import logging

from src.graph import build_graph, load_initial_state

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run automated book generation flow for a single book_id."
    )
    parser.add_argument(
        "--book-id",
        required=True,
        help="UUID of the book row in Supabase.",
    )
    args = parser.parse_args()

    logger.info(f"Starting book generation flow for book_id: {args.book_id}")

    workflow = build_graph()
    state = load_initial_state(args.book_id)
    logger.info(f"Loaded book: '{state.title}'")

    # Run the graph until completion or pause
    logger.info("Running workflow...")
    final_state = workflow.invoke(state)

    logger.info("Flow finished.")
    logger.info(f"Final event: {final_state.control.get('event')}")
    logger.info(f"Output status: {final_state.book_output_status}")


if __name__ == "__main__":
    main()

