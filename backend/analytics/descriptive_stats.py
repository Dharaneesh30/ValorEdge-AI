import pandas as pd


class DescriptiveStats:
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

    def compute(self):
        # include all columns for high-level summary
        result = self.data.describe(include='all').fillna('').to_dict()

        # convert numpy values to native types
        def normalize(v):
            if isinstance(v, (pd.Series, pd.Index)):
                return v.tolist()
            if hasattr(v, 'item'):
                try:
                    return v.item()
                except Exception:
                    pass
            return v

        return {k: {kk: normalize(vv) for kk, vv in v.items()} for k, v in result.items()}
