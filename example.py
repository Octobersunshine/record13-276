import pandas as pd
from multi_column_sorter import MultiColumnSorter, sort_dataframe


def create_sample_data():
    """创建示例数据"""
    data = {
        '部门': ['技术部', '市场部', '技术部', '市场部', '销售部', '技术部'],
        '姓名': ['张三', '李四', '王五', '赵六', '钱七', '孙八'],
        '年龄': [28, 32, 25, 35, 30, 28],
        '薪资': [15000, 12000, 18000, 13000, 16000, 17000],
        '入职日期': pd.to_datetime([
            '2020-03-15', '2019-08-20', '2021-01-10',
            '2018-11-05', '2020-06-30', '2022-02-28'
        ])
    }
    return pd.DataFrame(data)


def example_1_basic_sort():
    """示例1: 单列排序"""
    print("=" * 60)
    print("示例1: 单列排序 - 按薪资降序排列")
    print("=" * 60)
    df = create_sample_data()
    print("原始数据:")
    print(df)
    print("\n" + "-" * 60)

    sorter = MultiColumnSorter()
    result = sorter.sort(df, sort_columns='薪资', ascending=False)
    print("按薪资降序排列结果:")
    print(result)
    print()


def example_2_multi_column_sort():
    """示例2: 多列排序"""
    print("=" * 60)
    print("示例2: 多列排序 - 先按部门升序，再按薪资降序")
    print("=" * 60)
    df = create_sample_data()
    print("原始数据:")
    print(df)
    print("\n" + "-" * 60)

    sorter = MultiColumnSorter()
    result = sorter.sort(
        df,
        sort_columns=['部门', '薪资'],
        ascending=[True, False]
    )
    print("按部门升序、薪资降序排列结果:")
    print(result)
    print()

    cols, orders = sorter.get_last_sort_info()
    print(f"上一次排序列:", cols)
    print("上一次排序顺序:", ["升序" if o else "降序" for o in orders])
    print()


def example_3_sort_by_config():
    """示例3: 通过配置排序"""
    print("=" * 60)
    print("示例3: 通过配置列表排序")
    print("=" * 60)
    df = create_sample_data()
    print("原始数据:")
    print(df)
    print("\n" + "-" * 60)

    config = [
        {'column': '年龄', 'ascending': False},
        {'column': '薪资', 'ascending': False}
    ]

    sorter = MultiColumnSorter()
    result = sorter.sort_by_config(df, config)
    print("按年龄降序、薪资降序排列结果:")
    print(result)
    print()


def example_4_sort_with_key():
    """示例4: 带自定义 key 的排序"""
    print("=" * 60)
    print("示例4: 带自定义转换函数的排序")
    print("=" * 60)

    data = {
        'name': ['Alice', 'bob', 'Charlie', 'david', 'Eve'],
        'score': [85, 92, 78, 90, 88]
    }
    df = pd.DataFrame(data)
    print("原始数据:")
    print(df)
    print("\n" + "-" * 60)

    sorter = MultiColumnSorter()
    result = sorter.sort_with_key(
        df,
        sort_columns=['name'],
        ascending=True,
        key={'name': str.lower}
    )
    print("不区分大小写的姓名排序结果:")
    print(result)
    print()


def example_5_na_position():
    """示例5: 缺失值处理"""
    print("=" * 60)
    print("示例5: 缺失值位置处理")
    print("=" * 60)

    data = {
        '类别': ['A', 'B', None, 'A', 'B', 'A'],
        '数值': [10, 20, 30, None, 15, 25]
    }
    df = pd.DataFrame(data)
    print("原始数据（含缺失值）:")
    print(df)
    print("\n" + "-" * 60)

    sorter_last = MultiColumnSorter(na_position='last')
    result_last = sorter_last.sort(df, sort_columns=['类别', '数值'], ascending=[True, True])
    print("缺失值在后（默认）:")
    print(result_last)
    print()

    sorter_first = MultiColumnSorter(na_position='first')
    result_first = sorter_first.sort(df, sort_columns=['类别', '数值'], ascending=[True, True])
    print("缺失值在前:")
    print(result_first)
    print()


def example_6_convenience_function():
    """示例6: 使用便捷函数"""
    print("=" * 60)
    print("示例6: 使用便捷函数 sort_dataframe")
    print("=" * 60)
    df = create_sample_data()
    print("原始数据:")
    print(df)
    print("\n" + "-" * 60)

    result = sort_dataframe(
        df,
        sort_columns=['部门', '入职日期'],
        ascending=[True, False]
    )
    print("按部门升序、入职日期降序排列结果:")
    print(result)
    print()


def example_7_keep_index():
    """示例7: 保留原始索引"""
    print("=" * 60)
    print("示例7: 保留原始索引（不重置索引）")
    print("=" * 60)
    df = create_sample_data()
    print("原始数据:")
    print(df)
    print("\n" + "-" * 60)

    sorter = MultiColumnSorter()
    result_reset = sorter.sort(df, sort_columns='年龄', ascending=True, ignore_index=True)
    print("重置索引（默认）:")
    print(result_reset)
    print()

    result_keep = sorter.sort(df, sort_columns='年龄', ascending=True, ignore_index=False)
    print("保留原始索引:")
    print(result_keep)
    print()


def main():
    """运行所有示例"""
    example_1_basic_sort()
    example_2_multi_column_sort()
    example_3_sort_by_config()
    example_4_sort_with_key()
    example_5_na_position()
    example_6_convenience_function()
    example_7_keep_index()


if __name__ == "__main__":
    main()
