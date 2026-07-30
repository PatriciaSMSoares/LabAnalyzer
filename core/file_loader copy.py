import csv
import io
from pathlib import Path
import pandas as pd
import numpy as np



class FileParseError(Exception):
    pass

def _find_header(sample,delimeter):
    sample_last_line = sample.splitlines()[-2]  # Check 2nd to the last line

    #check How many columns are in the last line
    num_columns = len(sample_last_line.split(delimeter))

    #search for a line with the same number of columns
    for i, line in enumerate(sample.splitlines()):
        if len(line.split(delimeter)) == num_columns:
            if i > 0 :
                return i-1  # Return the index of the header line until the previous, so that I can have the good header line for the dataframe. The header line is the one before the first line with the same number of columns as the last line.
            else:
                return 0  # If the first line is the header, return None
            
    return 0


def detect_separator(sample):
    lines = [l for l in sample.splitlines() if l.strip()]

    # examine only the first few lines
    for line in lines[:20]:

        if line.count(",") >= 2:
            return ","

        if line.count(";") >= 2:
            return ";"

        if line.count("\t") >= 2:
            return "\t"

    # probably a whitespace table
    return r"\s{2,}"

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
            '.csv': self._parse_csv,
            '.txt': self._parse_text,
            '.dat': self._parse_text,
            '.xlsx': self._parse_excel,
            '.xls': self._parse_excel,
            '.fcd': self._parse_fcd,
            '.mpt': self._parse_eclab,
        }
        return parsers.get(ext, self._parse_text)

    def _parse_csv(self, path: Path) -> pd.DataFrame:
        """Auto-detect CSV delimiter using csv.Sniffer."""
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            sample = f.read(4096)

        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=',;\t| ')
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ','

    
        header = _find_header(sample, delimiter)

        print(f"header line detected at index: {header} for file: {path.name}")

        try:
            df = pd.read_csv(
                path,
                sep=delimiter,
                header=header,
                encoding='utf-8',
                encoding_errors='replace',
                skip_blank_lines=True,
                engine='python',
                quoting=csv.QUOTE_NONE,
            )
        except Exception:
            # fallback: try comma
            df = pd.read_csv(path, header=header, encoding='utf-8')

        df = self._clean_dataframe(df)

        return df

    def _parse_text(self, path: Path) -> pd.DataFrame:
        """Parse text/dat files, trying multiple delimiters."""
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            sample = f.read(4096)

        delimiter = detect_separator(sample)

        print(f"Detected delimiter '{delimiter}' for file: {path.name}")

        header = _find_header(sample, delimiter)

        print(f"header line detected at index: {header} for file: {path.name}")

        try:
            df = pd.read_csv(
                path,
                sep=delimiter,
                header=header,
                encoding='utf-8',
                encoding_errors='replace',
                skip_blank_lines=True,
                engine='python',
            )
        except Exception:
            df = pd.read_csv(path, sep=r'\s+', header=header, encoding='utf-8')

        df = self._clean_dataframe(df)

        print(df.head(10))

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
