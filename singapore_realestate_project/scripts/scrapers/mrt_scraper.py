"""
Singapore MRT Stations Scraper

Scrapes MRT station information from Wikipedia
https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations
"""

from bs4 import BeautifulSoup
import pandas as pd
import logging
import re
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class MRTScraper(BaseScraper):
    """Scraper for Singapore MRT station data from Wikipedia"""

    # Map substrings found in the Line column to short line codes.
    # Order matters: more specific strings should come before shorter ones
    # that could be substrings of them (e.g. "North East" before "East").
    LINE_MAPPING = [
        ("North–South",    "NS"),
        ("North-South",    "NS"),
        ("East–West",      "EW"),
        ("East-West",      "EW"),
        ("North East",     "NE"),
        ("North–East",     "NE"),
        ("North-East",     "NE"),
        ("Circle",         "CC"),   # matches both Circle Line and Circle Line Extension
        ("Downtown",       "DT"),
        ("Thomson",        "TE"),   # matches Thomson–East Coast Line
        ("Cross Island",   "CR"),
        ("Jurong Region",  "JR"),
        ("Branch Line",    "BL"),   # historical, no longer operational
    ]

    def __init__(self, headless=True, implicit_wait=10):
        """Initialize MRT scraper"""
        super().__init__(headless=headless, implicit_wait=implicit_wait)
        self.stations = []

    def scrape(self, url):
        """
        Scrape MRT stations from Wikipedia.

        Args:
            url: Wikipedia URL for MRT stations list

        Returns:
            pd.DataFrame: DataFrame containing MRT station data
        """
        self.setup_driver()
        try:
            self.get_page(url)
            page_source = self.driver.page_source
            self._extract_stations_from_source(page_source)
            return self.to_dataframe()
        finally:
            self.close_driver()

    def to_dataframe(self):
        """Convert scraped stations to DataFrame"""
        df = pd.DataFrame(self.stations)
        logger.info(f"Converted {len(df)} stations to DataFrame")
        return df

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------

    def _extract_stations_from_source(self, page_source):
        """Parse the raw HTML source with BeautifulSoup."""
        soup = BeautifulSoup(page_source, "html.parser")
        tables = soup.find_all("table", class_="wikitable")
        logger.info(f"Found {len(tables)} wikitable(s) on the page")

        for table_idx, table in enumerate(tables):
            logger.info(f"Processing table {table_idx + 1}")
            self._extract_from_table_bs4(table, table_idx)

        logger.info(f"Total stations extracted: {len(self.stations)}")

    def _expand_table(self, table):
        """
        Return a 2-D list of BeautifulSoup Tag objects that correctly accounts
        for rowspan and colspan attributes.

        Without this, rows that share a cell via rowspan would have their
        remaining cells at the wrong column indices.
        """
        grid = []
        # Maps col_index -> (remaining_rowspan_count, cell_tag)
        rowspan_carry: dict[int, tuple[int, object]] = {}

        for row in table.find_all("tr"):
            raw_cells = row.find_all(["th", "td"])
            expanded = []
            col = 0
            cell_iter = iter(raw_cells)

            while True:
                # First, fill any columns that are carried over from a rowspan
                while col in rowspan_carry:
                    remaining, carried_cell = rowspan_carry[col]
                    expanded.append(carried_cell)
                    if remaining - 1 > 0:
                        rowspan_carry[col] = (remaining - 1, carried_cell)
                    else:
                        del rowspan_carry[col]
                    col += 1

                # Then consume the next actual cell from this row
                try:
                    cell = next(cell_iter)
                except StopIteration:
                    break

                expanded.append(cell)
                rowspan = int(cell.get("rowspan", 1))
                colspan = int(cell.get("colspan", 1))

                # Register future rowspan carries for each spanned column
                if rowspan > 1:
                    for i in range(colspan):
                        rowspan_carry[col + i] = (rowspan - 1, cell)

                col += colspan

            # Flush any remaining rowspan carries for columns beyond real cells
            while col in rowspan_carry:
                remaining, carried_cell = rowspan_carry[col]
                expanded.append(carried_cell)
                if remaining - 1 > 0:
                    rowspan_carry[col] = (remaining - 1, carried_cell)
                else:
                    del rowspan_carry[col]
                col += 1

            grid.append(expanded)

        return grid

    def _extract_from_table_bs4(self, table, table_idx):
        """Extract station rows from a BeautifulSoup table element."""
        try:
            grid = self._expand_table(table)

            # First two rows are the merged column-group headers
            data_rows = grid[2:] if len(grid) > 2 else grid

            for row_cells in data_rows:
                try:
                    if len(row_cells) < 6:
                        continue

                    station_data = self._parse_bs4_row(row_cells)

                    if station_data["name"] and station_data["code"]:
                        self.stations.append(station_data)
                        logger.debug(
                            f"Extracted: {station_data['name']} "
                            f"({station_data['code']}) - {station_data['lines']}"
                        )

                except Exception as e:
                    logger.debug(f"Error parsing row: {e}")
                    continue

        except Exception as e:
            logger.warning(f"Error processing table {table_idx}: {e}")

    def _parse_bs4_row(self, cells):
        """
        Parse an expanded row (list of BS4 Tag objects) into a station dict.

        Expected column layout (after rowspan expansion):
          [0] English name
          [1] Chinese name
          [2] Tamil name
          [3] Station code  (e.g. "NS10")
          [4] Line(s)       (may contain multiple lines separated by <br>)
          [5] Opened date
          [6] Connections
          [7] References
        """
        station_data = {
            "name": "",
            "code": "",
            "lines": "",          # pipe-separated, e.g. "NS|CC"
            "opening_year": "",
            "latitude": "",
            "longitude": "",
        }

        def cell_text(cell):
            return cell.get_text(separator=" ", strip=True)

        # Col 0: English station name
        name = cell_text(cells[0])
        # Strip footnote markers like *, †, ‡, ^
        station_data["name"] = re.sub(r"[*†‡^]+$", "", name).strip()

        # Col 3: Station code — take the first code found (e.g. NS10, DT16)
        code_raw = cell_text(cells[3])
        code = self._extract_code_from_text(code_raw)
        if code:
            station_data["code"] = code

        # Col 4: Line(s) — use newline separator so each <br>-separated line
        #         is on its own line, making regex matching reliable
        line_raw = cells[4].get_text(separator="\n", strip=True)
        lines = self._extract_all_lines(line_raw)
        if lines:
            station_data["lines"] = lines

        # Col 5: Opening date
        date_raw = cell_text(cells[5])
        year = self._extract_year(date_raw)
        if year:
            station_data["opening_year"] = year

        return station_data

    # ------------------------------------------------------------------
    # Field-level extractors
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_code_from_text(text):
        """Extract the first station code (e.g. NS10, EW1, DT16) from text."""
        text = text.replace("\n", " ").strip()
        match = re.search(r"([A-Z]{2,3}\d+)", text)
        return match.group(1) if match else ""

    def _extract_all_lines(self, line_text):
        """
        Extract ALL line codes from a cell that may list several lines.

        The Wikipedia "Line" column uses <br> to separate multiple entries,
        which becomes newlines after get_text(separator="\\n").  We scan the
        text for every known line name and return the unique codes joined by
        a pipe character, e.g. "NS|CC" or "EW|DT".

        Lines marked "(under construction)" or "(planned)" are included so
        the data reflects what the Wikipedia table actually says; callers can
        filter on this if only operational lines are needed.
        """
        found = []
        seen: set[str] = set()
        for line_name, code in self.LINE_MAPPING:
            if line_name.lower() in line_text.lower() and code not in seen:
                found.append(code)
                seen.add(code)
        return "|".join(found)

    @staticmethod
    def _extract_year(text):
        """Extract the first 4-digit year (19xx or 20xx) from text."""
        match = re.search(r"\b(19|20)\d{2}\b", text)
        return match.group(0) if match else ""


# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scraper = MRTScraper(headless=True)
    url = "https://en.wikipedia.org/wiki/List_of_Singapore_MRT_stations"

    df = scraper.scrape(url)
    print(f"\nScraped {len(df)} MRT stations")
    print("\nFirst few stations:")
    print(df.head(10))

    # Save to CSV
    scraper.save_to_csv("data/raw/mrt_stations.csv")
