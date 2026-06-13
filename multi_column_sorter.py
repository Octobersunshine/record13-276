import pandas as pd
from typing import List, Tuple, Union, Optional, Dict, Any


class MultiColumnSorter:
    """
    基于 Pandas 的多列排序服务类。

    支持按指定列和顺序（升序/降序）对 DataFrame 进行排序，
    同时提供数据验证、缺失值处理等辅助功能。
    """

    def __init__(self, na_position: str = 'last'):
        """
        初始化排序器。

        Args:
            na_position: 缺失值的位置，'last'（默认）或 'first'
        """
        if na_position not in ['first', 'last']:
            raise ValueError("na_position 必须是 'first' 或 'last'")
        self.na_position = na_position
        self.last_sort_columns: List[str] = []
        self.last_sort_orders: List[bool] = []

    def sort(
        self,
        df: pd.DataFrame,
        sort_columns: Union[str, List[str]],
        ascending: Union[bool, List[bool]] = True,
        ignore_index: bool = True,
        inplace: bool = False
    ) -> Optional[pd.DataFrame]:
        """
        按指定列和排序方式对 DataFrame 进行排序。

        Args:
            df: 待排序的 DataFrame
            sort_columns: 排序列名，可以是单个字符串或列名列表
            ascending: 排序方式，可以是单个布尔值或布尔值列表，
                      True 为升序，False 为降序
            ignore_index: 是否重置索引，默认 True
            inplace: 是否在原 DataFrame 上修改，默认 False

        Returns:
            排序后的 DataFrame（inplace=False 时），否则返回 None

        Raises:
            ValueError: 列名不存在或参数不合法时抛出
        """
        sort_columns, ascending = self._validate_params(df, sort_columns, ascending)

        self.last_sort_columns = sort_columns
        self.last_sort_orders = ascending

        result = df.sort_values(
            by=sort_columns,
            ascending=ascending,
            na_position=self.na_position,
            ignore_index=ignore_index,
            inplace=inplace
        )

        return result

    def sort_by_config(
        self,
        df: pd.DataFrame,
        sort_config: List[Dict[str, Any]],
        ignore_index: bool = True,
        inplace: bool = False
    ) -> Optional[pd.DataFrame]:
        """
        通过配置列表进行排序。

        Args:
            df: 待排序的 DataFrame
            sort_config: 排序配置列表，每个元素为字典，格式为：
                        [{'column': '列名1', 'ascending': True},
                         {'column': '列名2', 'ascending': False}]
            ignore_index: 是否重置索引，默认 True
            inplace: 是否在原 DataFrame 上修改，默认 False

        Returns:
            排序后的 DataFrame（inplace=False 时），否则返回 None
        """
        columns = []
        orders = []

        for config in sort_config:
            if 'column' not in config:
                raise ValueError("排序配置必须包含 'column' 键")
            columns.append(config['column'])
            orders.append(config.get('ascending', True))

        return self.sort(
            df=df,
            sort_columns=columns,
            ascending=orders,
            ignore_index=ignore_index,
            inplace=inplace
        )

    def sort_with_key(
        self,
        df: pd.DataFrame,
        sort_columns: Union[str, List[str]],
        ascending: Union[bool, List[bool]] = True,
        key: Optional[Dict[str, callable]] = None,
        ignore_index: bool = True,
        inplace: bool = False
    ) -> Optional[pd.DataFrame]:
        """
        带自定义转换函数的排序。

        Args:
            df: 待排序的 DataFrame
            sort_columns: 排序列名，可以是单个字符串或列名列表
            ascending: 排序方式
            key: 列名到转换函数的映射字典，例如 {'name': str.lower}
            ignore_index: 是否重置索引，默认 True
            inplace: 是否在原 DataFrame 上修改，默认 False

        Returns:
            排序后的 DataFrame（inplace=False 时），否则返回 None
        """
        sort_columns, ascending = self._validate_params(df, sort_columns, ascending)
        self.last_sort_columns = sort_columns
        self.last_sort_orders = ascending

        if key is None:
            return self.sort(df, sort_columns, ascending, ignore_index, inplace)

        temp_df = df.copy()
        for col, func in key.items():
            if col in sort_columns:
                temp_df[f'__key_{col}'] = temp_df[col].apply(func)

        key_columns = [
            f'__key_{col}' if col in key else col
            for col in sort_columns
        ]

        result = temp_df.sort_values(
            by=key_columns,
            ascending=ascending,
            na_position=self.na_position,
            ignore_index=ignore_index,
            inplace=False
        )

        result = result.drop(columns=[c for c in result.columns if c.startswith('__key_')])

        if inplace:
            df.drop(df.index, inplace=True)
            df[result.columns] = result
            return None

        return result

    def get_last_sort_info(self) -> Tuple[List[str], List[bool]]:
        """
        获取上一次排序的列和顺序信息。

        Returns:
            (排序列名列表, 排序顺序列表)
        """
        return self.last_sort_columns, self.last_sort_orders

    def _validate_params(
        self,
        df: pd.DataFrame,
        sort_columns: Union[str, List[str]],
        ascending: Union[bool, List[bool]]
    ) -> Tuple[List[str], List[bool]]:
        """
        验证排序参数并标准化格式。

        Args:
            df: 待排序的 DataFrame
            sort_columns: 排序列名
            ascending: 排序方式

        Returns:
            (标准化后的列名列表, 标准化后的排序方式列表)

        Raises:
            ValueError: 参数不合法时抛出
        """
        if not isinstance(df, pd.DataFrame):
            raise ValueError("输入必须是 pandas DataFrame")

        if df.empty:
            raise ValueError("DataFrame 不能为空")

        if isinstance(sort_columns, str):
            sort_columns = [sort_columns]

        if not sort_columns:
            raise ValueError("排序列名不能为空")

        for col in sort_columns:
            if col not in df.columns:
                raise ValueError(f"列 '{col}' 不存在于 DataFrame 中，可用列: {list(df.columns)}")

        if isinstance(ascending, bool):
            ascending = [ascending] * len(sort_columns)

        if len(ascending) != len(sort_columns):
            raise ValueError(
                f"排序方式数量 ({len(ascending)}) 与排序列数量 ({len(sort_columns)}) 不匹配"
            )

        return sort_columns, ascending


def sort_dataframe(
    df: pd.DataFrame,
    sort_columns: Union[str, List[str]],
    ascending: Union[bool, List[bool]] = True,
    na_position: str = 'last',
    ignore_index: bool = True
) -> pd.DataFrame:
    """
    便捷函数：对 DataFrame 进行多列排序。

    Args:
        df: 待排序的 DataFrame
        sort_columns: 排序列名
        ascending: 排序方式
        na_position: 缺失值位置
        ignore_index: 是否重置索引

    Returns:
        排序后的 DataFrame
    """
    sorter = MultiColumnSorter(na_position=na_position)
    return sorter.sort(df, sort_columns, ascending, ignore_index, inplace=False)
