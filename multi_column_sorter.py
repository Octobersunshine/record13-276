import warnings
import pandas as pd
import numpy as np
from typing import List, Tuple, Union, Optional, Dict, Any


class MultiColumnSorter:
    """
    基于 Pandas 的多列排序服务类。

    支持按指定列和顺序（升序/降序）对 DataFrame 进行排序，
    同时提供数据验证、缺失值处理、混合类型自动转换等辅助功能。
    """

    def __init__(self, na_position: str = 'last', auto_convert_types: bool = True):
        """
        初始化排序器。

        Args:
            na_position: 缺失值的位置，'last'（默认）或 'first'
            auto_convert_types: 是否自动转换混合数据类型列（默认 True），
                               自动将 object 列尝试转换为数值或日期类型
        """
        if na_position not in ['first', 'last']:
            raise ValueError("na_position 必须是 'first' 或 'last'")
        self.na_position = na_position
        self.auto_convert_types = auto_convert_types
        self.last_sort_columns: List[str] = []
        self.last_sort_orders: List[bool] = []
        self.last_conversions: Dict[str, str] = {}
        self.last_custom_orders: Dict[str, List[Any]] = {}

    def sort(
        self,
        df: pd.DataFrame,
        sort_columns: Union[str, List[str]],
        ascending: Union[bool, List[bool]] = True,
        ignore_index: bool = True,
        inplace: bool = False,
        custom_orders: Optional[Dict[str, List[Any]]] = None
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
            custom_orders: 自定义排序规则字典，键为列名，值为自定义顺序列表，
                          例如 {'优先级': ['高', '中', '低']}，未在列表中的值排在末尾

        Returns:
            排序后的 DataFrame（inplace=False 时），否则返回 None

        Raises:
            ValueError: 列名不存在或参数不合法时抛出
        """
        sort_columns, ascending = self._validate_params(df, sort_columns, ascending)

        self.last_sort_columns = sort_columns
        self.last_sort_orders = ascending
        self.last_conversions = {}
        self.last_custom_orders = custom_orders or {}

        temp_df = df.copy()
        all_temp_cols: List[str] = []
        sort_key_columns = list(sort_columns)

        if custom_orders:
            custom_temp_cols = self._apply_custom_orders(temp_df, custom_orders, sort_columns)
            all_temp_cols.extend(custom_temp_cols.values())
            sort_key_columns = [
                custom_temp_cols[col] if col in custom_temp_cols else col
                for col in sort_key_columns
            ]

        if self.auto_convert_types:
            converted_map, auto_temp_columns = self._auto_convert_columns(temp_df, sort_key_columns)
            self.last_conversions = converted_map

            if auto_temp_columns:
                for col, temp_col in auto_temp_columns.items():
                    temp_df[temp_col] = converted_map[col + '__values']
                    all_temp_cols.append(temp_col)
                sort_key_columns = [
                    auto_temp_columns[col] if col in auto_temp_columns else col
                    for col in sort_key_columns
                ]

        result = temp_df.sort_values(
            by=sort_key_columns,
            ascending=ascending,
            na_position=self.na_position,
            ignore_index=ignore_index,
            inplace=False
        )

        if all_temp_cols:
            result = result.drop(columns=all_temp_cols)

        if inplace:
            df.drop(df.index, inplace=True)
            df[result.columns] = result
            return None

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
                         {'column': '列名2', 'ascending': False, 'order': ['高', '中', '低']}]
                        其中 'order' 为可选字段，用于指定该列的自定义排序顺序
            ignore_index: 是否重置索引，默认 True
            inplace: 是否在原 DataFrame 上修改，默认 False

        Returns:
            排序后的 DataFrame（inplace=False 时），否则返回 None
        """
        columns = []
        orders = []
        custom_orders: Dict[str, List[Any]] = {}

        for config in sort_config:
            if 'column' not in config:
                raise ValueError("排序配置必须包含 'column' 键")
            col = config['column']
            columns.append(col)
            orders.append(config.get('ascending', True))
            if 'order' in config:
                custom_orders[col] = config['order']

        return self.sort(
            df=df,
            sort_columns=columns,
            ascending=orders,
            ignore_index=ignore_index,
            inplace=inplace,
            custom_orders=custom_orders if custom_orders else None
        )

    def sort_with_custom_order(
        self,
        df: pd.DataFrame,
        sort_columns: Union[str, List[str]],
        custom_orders: Dict[str, List[Any]],
        ascending: Union[bool, List[bool]] = True,
        ignore_index: bool = True,
        inplace: bool = False
    ) -> Optional[pd.DataFrame]:
        """
        按自定义顺序对指定列进行排序的便捷方法。

        Args:
            df: 待排序的 DataFrame
            sort_columns: 排序列名，可以是单个字符串或列名列表
            custom_orders: 自定义排序规则字典，键为列名，值为自定义顺序列表
            ascending: 排序方式，默认 True（升序）
            ignore_index: 是否重置索引，默认 True
            inplace: 是否在原 DataFrame 上修改，默认 False

        Returns:
            排序后的 DataFrame（inplace=False 时），否则返回 None
        """
        return self.sort(
            df=df,
            sort_columns=sort_columns,
            ascending=ascending,
            ignore_index=ignore_index,
            inplace=inplace,
            custom_orders=custom_orders
        )

    def sort_with_key(
        self,
        df: pd.DataFrame,
        sort_columns: Union[str, List[str]],
        ascending: Union[bool, List[bool]] = True,
        key: Optional[Dict[str, callable]] = None,
        ignore_index: bool = True,
        inplace: bool = False,
        custom_orders: Optional[Dict[str, List[Any]]] = None
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
            custom_orders: 自定义排序规则字典

        Returns:
            排序后的 DataFrame（inplace=False 时），否则返回 None
        """
        sort_columns, ascending = self._validate_params(df, sort_columns, ascending)
        self.last_sort_columns = sort_columns
        self.last_sort_orders = ascending
        self.last_conversions = {}
        self.last_custom_orders = custom_orders or {}

        if key is None:
            return self.sort(df, sort_columns, ascending, ignore_index, inplace, custom_orders)

        temp_df = df.copy()
        all_temp_cols: List[str] = []
        sort_key_columns = list(sort_columns)

        if custom_orders:
            custom_temp_cols = self._apply_custom_orders(temp_df, custom_orders, sort_columns)
            all_temp_cols.extend(custom_temp_cols.values())
            sort_key_columns = [
                custom_temp_cols[col] if col in custom_temp_cols else col
                for col in sort_key_columns
            ]

        key_temp_cols: Dict[str, str] = {}
        for col, func in key.items():
            if col in sort_key_columns:
                temp_col = f'__key_{col}'
                temp_df[temp_col] = temp_df[col].apply(func)
                all_temp_cols.append(temp_col)
                key_temp_cols[col] = temp_col

        sort_key_columns = [
            key_temp_cols[col] if col in key_temp_cols else col
            for col in sort_key_columns
        ]

        auto_converted_map: Dict[str, Any] = {}
        auto_temp_columns: Dict[str, str] = {}
        if self.auto_convert_types:
            auto_converted_map, auto_temp_columns = self._auto_convert_columns(temp_df, sort_key_columns)
            self.last_conversions = auto_converted_map
            for col, temp_col in auto_temp_columns.items():
                temp_df[temp_col] = auto_converted_map[col + '__values']
                all_temp_cols.append(temp_col)
            sort_key_columns = [
                auto_temp_columns[col] if col in auto_temp_columns else col
                for col in sort_key_columns
            ]

        result = temp_df.sort_values(
            by=sort_key_columns,
            ascending=ascending,
            na_position=self.na_position,
            ignore_index=ignore_index,
            inplace=False
        )

        result = result.drop(columns=all_temp_cols)

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

    def get_last_conversions(self) -> Dict[str, str]:
        """
        获取上一次排序中各列的类型转换信息。

        Returns:
            字典，键为列名，值为转换后的目标类型（如 'numeric', 'datetime'），
            未转换的列不在返回结果中
        """
        return {k: v for k, v in self.last_conversions.items() if not k.endswith('__values')}

    def get_last_custom_orders(self) -> Dict[str, List[Any]]:
        """
        获取上一次排序的自定义排序规则。

        Returns:
            字典，键为列名，值为自定义顺序列表
        """
        return self.last_custom_orders

    def _apply_custom_orders(
        self,
        df: pd.DataFrame,
        custom_orders: Dict[str, List[Any]],
        sort_columns: List[str]
    ) -> Dict[str, str]:
        """
        为指定列应用自定义排序规则，通过 Categorical 类型实现。

        Args:
            df: 待处理的 DataFrame（会被原地修改）
            custom_orders: 自定义排序规则字典
            sort_columns: 排序列名列表

        Returns:
            列名到临时列名的映射字典
        """
        temp_columns: Dict[str, str] = {}

        for col, order in custom_orders.items():
            if col not in sort_columns:
                continue

            if not order:
                raise ValueError(f"列 '{col}' 的自定义排序顺序列表不能为空")

            temp_col_name = f'__custom_order_{col}'
            order_map = {val: idx for idx, val in enumerate(order)}
            max_idx = len(order)
            df[temp_col_name] = df[col].map(lambda x: order_map.get(x, max_idx) if pd.notna(x) else np.nan)
            temp_columns[col] = temp_col_name

        return temp_columns

    def _auto_convert_columns(
        self,
        df: pd.DataFrame,
        sort_columns: List[str]
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        自动检测并转换排序列的数据类型。

        对 object 类型的列，优先尝试转换为数值类型，其次尝试转换为日期类型。
        转换结果通过临时列保存，不修改原始数据。

        Args:
            df: 待排序的 DataFrame
            sort_columns: 排序列名列表

        Returns:
            (转换信息字典, 列名到临时列名的映射字典)
            转换信息字典包含类型名称和转换后的值数组
        """
        converted_map: Dict[str, Any] = {}
        temp_columns: Dict[str, str] = {}

        for col in sort_columns:
            series = df[col]
            dtype_str = str(series.dtype).lower()

            if dtype_str not in ('object', 'string', 'str'):
                continue

            non_null = series.dropna()
            if non_null.empty:
                continue

            converted, target_type = self._try_convert_series(series)
            if converted is not None and target_type is not None:
                temp_col_name = f'__auto_convert_{col}'
                temp_columns[col] = temp_col_name
                converted_map[col] = target_type
                converted_map[col + '__values'] = converted

        return converted_map, temp_columns

    def _try_convert_series(self, series: pd.Series) -> Tuple[Optional[pd.Series], Optional[str]]:
        """
        尝试转换 Series 的数据类型。

        转换优先级：数值 > 日期
        只有当非空值的转换成功率 >= 80% 时才认为转换有效。

        Args:
            series: 待转换的 Series

        Returns:
            (转换后的 Series, 目标类型名称)，转换失败时返回 (None, None)
        """
        non_null_mask = series.notna()
        non_null_count = non_null_mask.sum()

        if non_null_count == 0:
            return None, None

        min_success_ratio = 0.8

        numeric_converted = self._try_convert_numeric(series, non_null_mask)
        if numeric_converted is not None:
            success_count = numeric_converted[non_null_mask].notna().sum()
            if success_count / non_null_count >= min_success_ratio:
                return numeric_converted, 'numeric'

        datetime_converted = self._try_convert_datetime(series, non_null_mask)
        if datetime_converted is not None:
            success_count = datetime_converted[non_null_mask].notna().sum()
            if success_count / non_null_count >= min_success_ratio:
                return datetime_converted, 'datetime'

        return None, None

    def _try_convert_numeric(
        self,
        series: pd.Series,
        non_null_mask: pd.Series
    ) -> Optional[pd.Series]:
        """
        尝试将 Series 转换为数值类型。

        Args:
            series: 待转换的 Series
            non_null_mask: 非空值掩码

        Returns:
            转换后的 Series，转换失败时返回 None
        """
        try:
            non_null_values = series[non_null_mask]

            if non_null_values.apply(lambda x: isinstance(x, (int, float, np.integer, np.floating))).all():
                return pd.to_numeric(series, errors='coerce')

            converted = pd.to_numeric(series, errors='coerce')
            if converted[non_null_mask].notna().any():
                return converted
            return None
        except (ValueError, TypeError):
            return None

    def _try_convert_datetime(
        self,
        series: pd.Series,
        non_null_mask: pd.Series
    ) -> Optional[pd.Series]:
        """
        尝试将 Series 转换为日期类型。

        Args:
            series: 待转换的 Series
            non_null_mask: 非空值掩码

        Returns:
            转换后的 Series，转换失败时返回 None
        """
        try:
            non_null_values = series[non_null_mask]

            if non_null_values.apply(lambda x: isinstance(x, (pd.Timestamp, np.datetime64))).all():
                return pd.to_datetime(series, errors='coerce')

            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                converted = pd.to_datetime(series, errors='coerce')

            if converted[non_null_mask].notna().any():
                return converted
            return None
        except (ValueError, TypeError):
            return None

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
    ignore_index: bool = True,
    auto_convert_types: bool = True,
    custom_orders: Optional[Dict[str, List[Any]]] = None
) -> pd.DataFrame:
    """
    便捷函数：对 DataFrame 进行多列排序。

    Args:
        df: 待排序的 DataFrame
        sort_columns: 排序列名
        ascending: 排序方式
        na_position: 缺失值位置
        ignore_index: 是否重置索引
        auto_convert_types: 是否自动转换混合数据类型列（默认 True）
        custom_orders: 自定义排序规则字典，例如 {'优先级': ['高', '中', '低']}

    Returns:
        排序后的 DataFrame
    """
    sorter = MultiColumnSorter(na_position=na_position, auto_convert_types=auto_convert_types)
    return sorter.sort(df, sort_columns, ascending, ignore_index, inplace=False, custom_orders=custom_orders)
