import csv
import io
from collections import Counter
from pathlib import Path
import re
import pandas as pd
import numpy as np



class FileParseError(Exception):
    pass


# Candidate delimiters for generic delimited-table detection, in
# preference order when there's a tie in split-consistency. The
# whitespace pattern uses 2+ spaces (not \s+) so that multi-word
# column labels with a single internal space (e.g. "% Volume") don't
# get split apart, while still separating columns that are visually
# spaced apart in a fixed-width report.
_DELIMITER_CANDIDATES = [',', ';', '\t', '|', r'\s{2,}']

_NUMERIC_RE = re.compile(r'^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$')


def _split_line(line: str, delimiter: str):
    """Split a line by a candidate delimiter, whitespace-aware."""
    stripped = line.strip('\r\n')
    if delimiter == r'\s{2,}':
        stripped = stripped.strip()
        if not stripped:
            return []
        return re.split(r'\s{2,}', stripped)
    return [t for t in stripped.split(delimiter)]


def _is_numeric_token(token: str) -> bool:
    return bool(_NUMERIC_RE.match(token.strip()))


def detect_table_layout(lines):
    """Generically figure out how to read a delimited/fixed-width table.

    Works for plain single-delimiter CSVs as well as instrument-style
    text reports that have a metadata/comment block and a header
    wrapped across multiple lines before the numeric data starts.
    Returns a dict with: delimiter, n_cols, data_start (line index of
    the first data row), and columns (list of column names).
    Returns None if no consistent tabular block could be found.
    """
    non_blank = [(i, l) for i, l in enumerate(lines) if l.strip()]
    if not non_blank:
        return None

    # 1. Pick the delimiter whose line-splits are most consistent, i.e.
    #    the one where the largest fraction of non-blank lines share the
    #    same field count (the "mode"). This replaces a fixed "needs 2+
    #    occurrences" heuristic, which breaks on ordinary 2-column files
    #    (only 1 delimiter occurrence per line).
    best = None  # (consistency, -pref_index, delimiter, n_cols)
    for pref_index, delim in enumerate(_DELIMITER_CANDIDATES):
        counts = [len(_split_line(l, delim)) for _, l in non_blank]
        counts = [c for c in counts if c > 1]
        if not counts:
            continue
        mode_count, mode_freq = Counter(counts).most_common(1)[0]
        consistency = mode_freq / len(non_blank)
        key = (consistency, -pref_index)
        if best is None or key > (best[0], -best[1]):
            best = (consistency, pref_index, delim, mode_count)
    if best is None:
        return None
    _, _, delimiter, n_cols = best

    # 2. Find where the numeric data actually starts: the first line
    #    that splits into n_cols fields where most fields are numeric,
    #    and which is followed by more lines doing the same (so a
    #    header row that happens to also have n_cols fields doesn't get
    #    mistaken for data).
    def matches_data_row(line):
        fields = _split_line(line, delimiter)
        if len(fields) != n_cols:
            return False
        numeric_fields = sum(_is_numeric_token(f) for f in fields)
        return numeric_fields >= max(1, len(fields) - 1)  # allow one label/text field

    data_start = None
    for idx, (i, line) in enumerate(non_blank):
        if not matches_data_row(line):
            continue
        # confirm with a short lookahead so we don't latch onto a stray line
        lookahead = non_blank[idx: idx + 3]
        if sum(matches_data_row(l) for _, l in lookahead) >= min(2, len(lookahead)):
            data_start = i
            break
    if data_start is None:
        return None

    # 3. Collect the header block: contiguous non-blank lines
    #    immediately above the data start (stopping at the first blank
    #    line or the top of the file).
    header_lines = []
    i = data_start - 1
    while i >= 0 and not lines[i].strip():
        i -= 1  # skip a single blank separator line right above the data
    while i >= 0 and lines[i].strip():
        header_lines.append(lines[i])
        i -= 1
    header_lines.reverse()

    # 4. Build column names generically: use every header line whose
    #    field count matches n_cols (name row, units row, etc.) and
    #    join the tokens at each column position. Lines that don't
    #    match n_cols (e.g. a wrapped continuation line) are skipped
    #    rather than guessed at.
    qualifying_rows = [
        _split_line(hl, delimiter) for hl in header_lines
        if len(_split_line(hl, delimiter)) == n_cols
    ]
    if qualifying_rows:
        columns = []
        for col_idx in range(n_cols):
            parts = [row[col_idx].strip() for row in qualifying_rows if row[col_idx].strip()]
            columns.append(' '.join(parts) if parts else f'Column_{col_idx}')
    else:
        columns = [f'Column_{i}' for i in range(n_cols)]

    return {
        'delimiter': delimiter,
        'n_cols': n_cols,
        'data_start': data_start,
        'columns': columns,
    }


class FileLoader:
    """Loads various data file types into pandas DataFrames."""

    SUPPORTED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.txt', '.dat', '.fcd', '.mpt'}

    def load(self, path: Path) -> pd.DataFrame:
        """Load a file and return a DataFrame."""
        path = Path(path)
        if not path.exists():
            raise FileParseError(f"File not found: {path}")

        ext = path.suffix.lower()
        parser = self._get_parser(ext)
        try:
            df = parser(path)
            return df
        except FileParseError:
            raise
        except Exception as e:
            raise FileParseError(f"Failed to parse {path.name}: {e}") from e

    def _get_parser(self, ext: str):
        parsers = {
            '.csv': self._parse_delimited,
            '.txt': self._parse_delimited,
            '.dat': self._parse_delimited,
            '.xlsx': self._parse_excel,
            '.xls': self._parse_excel,
            '.fcd': self._parse_fcd,
            '.mpt': self._parse_eclab,
        }
        return parsers.get(ext, self._parse_delimited)

    def _parse_delimited(self, path: Path) -> pd.DataFrame:
        """Generic parser for CSV/TSV/whitespace-delimited text files.

        Handles both plain single-header delimited tables and
        instrument-style reports where a metadata block and a header
        wrapped across multiple lines precede the actual numeric data
        -- all via the same layout-detection logic, rather than a
        format-specific parser per instrument.
        """
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        layout = detect_table_layout(lines)
        if layout is None:
            raise FileParseError(f"Could not detect a tabular structure in {path.name}")

        print(
            f"{path.name}: delimiter={layout['delimiter']!r} n_cols={layout['n_cols']} "
            f"data_start_line={layout['data_start']} columns={layout['columns']}"
        )

        data_text = ''.join(lines[layout['data_start']:])
        sep = layout['delimiter']
        try:
            df = pd.read_csv(
                io.StringIO(data_text),
                sep=sep,
                header=None,
                names=layout['columns'],
                engine='python',
                skip_blank_lines=True,
                quoting=csv.QUOTE_NONE if sep in (',', ';', '\t', '|') else csv.QUOTE_MINIMAL,
            )
        except Exception:
            # last-resort fallback: split on any whitespace
            df = pd.read_csv(
                io.StringIO(data_text), sep=r'\s+', header=None,
                names=layout['columns'], engine='python',
            )

        df = self._clean_dataframe(df)
        return df

    def _parse_excel(self, path: Path) -> pd.DataFrame:
        """Parse Excel files using openpyxl/xlrd via pandas."""
        try:
            df = pd.read_excel(path, sheet_name=0, header=0)
        except Exception as e:
            raise FileParseError(f"Excel parse error: {e}") from e
        df = self._clean_dataframe(df)
        return df

    def _parse_fcd(self, path: Path) -> pd.DataFrame:
        """Parse FuelCell .fcd files with custom header ending at 'End Comments'."""
        FCD_COLUMNS = [
            'Time (Sec)', 'I (A)', 'I (mA/cm²)', 'Power (Watts)', 'Power (mW/cm²)',
            'E_Stack (V)', 'E_Comp_Stack (V)', 'E_iR_Stack (V)', 'E_iR_Stack (mOhm)',
            'E_iR_Avg (mOhm*cm²)', 'Temp (C)', 'Temp_Anode (C)', 'Temp_Cathode (C)',
            'Flow_Anode (l/min)', 'Flow_Cathode (l/min)', 'RH_Anode (%)', 'RH_Cathode (%)',
            'HFR (mOhm)', 'HFR (mOhm*cm²)'
        ]
        lines = []
        past_header = False
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                if not past_header:
                    if line.strip() == 'End Comments':
                        past_header = True
                    continue
                lines.append(line)
        if not lines:
            raise FileParseError(f"No data found in {path.name}")
        text = ''.join(lines)
        df = pd.read_csv(io.StringIO(text), sep='\t', header=None,
                         names=FCD_COLUMNS[:19], engine='python')
        df = self._clean_dataframe(df)
        return df

    def _parse_eclab(self, path: Path) -> pd.DataFrame:
        """Parse EC-Lab .mpt and .sta files with 'Nb header lines' header."""
        # Detect binary files (EC-Lab .sta can be binary format)
        with open(path, 'rb') as fb:
            header_bytes = fb.read(512)
        if b'\x00' in header_bytes:
            raise FileParseError(
                f"{path.name} is a binary EC-Lab file (.sta binary format) and cannot be parsed as text. "
                "Export the file as .mpt (ASCII) from EC-Lab to load it."
            )
        with open(path, 'r', encoding='latin-1', errors='replace') as f:
            lines = f.readlines()
        nb_header = None
        for line in lines[:5]:
            if 'Nb header lines' in line:
                parts = line.split(':')
                nb_header = int(parts[1].strip().split()[0])
                break
        if nb_header is None:
            raise FileParseError(f"Could not parse EC-Lab header in {path.name}")
        header_line = lines[nb_header - 1].strip().replace('\r', '')
        columns = [c.strip() for c in header_line.split('\t')]
        data_lines = lines[nb_header:]
        text = ''.join(data_lines)
        df = pd.read_csv(io.StringIO(text), sep='\t', header=None, names=columns,
                         engine='python', on_bad_lines='skip')
        df = self._clean_dataframe(df)
        return df

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean up a loaded DataFrame."""
        # Strip whitespace from column names
        df.columns = [str(c).strip() for c in df.columns]

        # Rename unnamed columns
        df.columns = [
            f'Column_{i}' if col.startswith('Unnamed') else col
            for i, col in enumerate(df.columns)
        ]

        # Try to convert all columns to numeric where possible
        for col in df.columns:
            try:
                converted = pd.to_numeric(df[col], errors='coerce')
                # If standard conversion fails for most values, try comma-as-decimal
                if converted.notna().sum() < df[col].notna().sum() * 0.5:
                    converted = pd.to_numeric(
                        df[col].astype(str).str.replace(',', '.', regex=False),
                        errors='coerce',
                    )
                if converted.notna().sum() >= df[col].notna().sum() * 0.5:
                    df[col] = converted
            except Exception:
                pass

        # Drop fully empty rows
        df.dropna(how='all', inplace=True)
        df.reset_index(drop=True, inplace=True)

        return df
