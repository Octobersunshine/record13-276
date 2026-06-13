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


def example_8_mixed_numeric_sort():
    """示例8: 混合数值类型排序修复"""
    print("=" * 60)
    print("示例8: 数字与字符串数字混合排序（自动类型转换）")
    print("=" * 60)

    data = {
        'name': ['A', 'B', 'C', 'D', 'E'],
        'mixed_num': [10, '5', 20, '15', 3]
    }
    df = pd.DataFrame(data)
    print("原始数据（数字和字符串数字混合）:")
    print(df)
    print(f"mixed_num 列类型: {df['mixed_num'].dtype}")
    print("\n" + "-" * 60)

    sorter = MultiColumnSorter()
    result = sorter.sort(df, sort_columns='mixed_num', ascending=True)
    print("自动转换类型后的升序排序结果:")
    print(result)
    print("类型转换信息:", sorter.get_last_conversions())
    print()

    print("-" * 60)
    print("关闭自动转换（会报错）:")
    try:
        sorter_no_convert = MultiColumnSorter(auto_convert_types=False)
        result_no = sorter_no_convert.sort(df, sort_columns='mixed_num', ascending=True)
        print(result_no)
    except TypeError as e:
        print(f"TypeError: {e}")
    print()


def example_9_mixed_datetime_sort():
    """示例9: 混合日期类型排序修复"""
    print("=" * 60)
    print("示例9: Timestamp与字符串日期混合排序（自动类型转换）")
    print("=" * 60)

    data = {
        'name': ['A', 'B', 'C', 'D'],
        'mixed_date': [
            pd.Timestamp('2023-01-15'),
            '2022-06-30',
            pd.Timestamp('2024-03-20'),
            '2023-09-01'
        ]
    }
    df = pd.DataFrame(data)
    print("原始数据（Timestamp和字符串日期混合）:")
    print(df)
    print(f"mixed_date 列类型: {df['mixed_date'].dtype}")
    print("\n" + "-" * 60)

    sorter = MultiColumnSorter()
    result = sorter.sort(df, sort_columns='mixed_date', ascending=True)
    print("自动转换类型后的升序排序结果:")
    print(result)
    print("类型转换信息:", sorter.get_last_conversions())
    print()


def example_10_multi_column_mixed_sort():
    """示例10: 多列混合类型排序"""
    print("=" * 60)
    print("示例10: 多列混合类型排序")
    print("=" * 60)

    data = {
        'category': ['X', 'Y', 'X', 'Y', 'X'],
        'mixed_num': ['100', 50, 200, '80', 150],
        'mixed_date': [
            '2023-05-01',
            pd.Timestamp('2022-12-15'),
            '2024-01-10',
            pd.Timestamp('2023-08-20'),
            '2023-02-28'
        ],
        'value': [1, 2, 3, 4, 5]
    }
    df = pd.DataFrame(data)
    print("原始数据:")
    print(df)
    print("\n" + "-" * 60)

    sorter = MultiColumnSorter()
    result = sorter.sort(
        df,
        sort_columns=['category', 'mixed_num', 'mixed_date'],
        ascending=[True, True, False]
    )
    print("按 category升序、mixed_num升序、mixed_date降序 排序结果:")
    print(result)
    print("类型转换信息:", sorter.get_last_conversions())
    print()


def example_11_string_numeric_lexicographic_fix():
    """示例11: 字符串数字词典序问题修复"""
    print("=" * 60)
    print("示例11: 字符串数字词典序问题修复")
    print("=" * 60)

    data = {
        'code': ['10', '2', '100', '15', '3', '20']
    }
    df = pd.DataFrame(data)
    print("原始数据（纯字符串数字）:")
    print(df)
    print(f"code 列类型: {df['code'].dtype}")
    print("\n" + "-" * 60)

    result_naive = df.sort_values('code')
    print("Pandas 默认排序（词典序，错误）:")
    print(result_naive)
    print()

    sorter = MultiColumnSorter()
    result_fixed = sorter.sort(df, sort_columns='code', ascending=True)
    print("自动转换后的正确排序（数值序）:")
    print(result_fixed)
    print("类型转换信息:", sorter.get_last_conversions())
    print()


def example_12_custom_order_basic():
    """示例12: 基础自定义排序 - 按高/中/低排序"""
    print("=" * 60)
    print("示例12: 基础自定义排序 - 按优先级 高→中→低 排序")
    print("=" * 60)

    data = {
        '任务': ['A', 'B', 'C', 'D', 'E', 'F'],
        '优先级': ['中', '高', '低', '高', '中', '低'],
        '完成度': [80, 95, 60, 70, 85, 40]
    }
    df = pd.DataFrame(data)
    print("原始数据:")
    print(df)
    print("\n" + "-" * 60)

    sorter = MultiColumnSorter()
    custom_orders = {'优先级': ['高', '中', '低']}
    result = sorter.sort(df, sort_columns='优先级', ascending=True, custom_orders=custom_orders)
    print("按 高→中→低 排序结果:")
    print(result)
    print("自定义规则:", sorter.get_last_custom_orders())
    print()


def example_13_custom_order_with_other_cols():
    """示例13: 多列混合排序 - 自定义规则 + 普通升序"""
    print("=" * 60)
    print("示例13: 多列混合排序 - 优先级(自定义) + 完成度(降序)")
    print("=" * 60)

    data = {
        '任务': ['A', 'B', 'C', 'D', 'E', 'F'],
        '优先级': ['中', '高', '低', '高', '中', '低'],
        '完成度': [80, 95, 60, 70, 85, 40]
    }
    df = pd.DataFrame(data)
    print("原始数据:")
    print(df)
    print("\n" + "-" * 60)

    sorter = MultiColumnSorter()
    custom_orders = {'优先级': ['高', '中', '低']}
    result = sorter.sort(
        df,
        sort_columns=['优先级', '完成度'],
        ascending=[True, False],
        custom_orders=custom_orders
    )
    print("按 优先级(高→中→低)、完成度(高→低) 排序结果:")
    print(result)
    print()


def example_14_custom_order_multiple_cols():
    """示例14: 多列均使用自定义排序"""
    print("=" * 60)
    print("示例14: 多列自定义排序 - 部门 + 职级")
    print("=" * 60)

    data = {
        '姓名': ['张三', '李四', '王五', '赵六', '钱七', '孙八'],
        '部门': ['市场部', '技术部', '技术部', '销售部', '市场部', '技术部'],
        '职级': ['P6', 'P7', 'P5', 'P6', 'P5', 'P6'],
        '薪资': [15000, 25000, 12000, 18000, 13000, 18000]
    }
    df = pd.DataFrame(data)
    print("原始数据:")
    print(df)
    print("\n" + "-" * 60)

    sorter = MultiColumnSorter()
    custom_orders = {
        '部门': ['技术部', '市场部', '销售部'],
        '职级': ['P7', 'P6', 'P5']
    }
    result = sorter.sort(
        df,
        sort_columns=['部门', '职级'],
        ascending=[True, True],
        custom_orders=custom_orders
    )
    print("按 部门(技术部→市场部→销售部)、职级(P7→P6→P5) 排序结果:")
    print(result)
    print("自定义规则:", sorter.get_last_custom_orders())
    print()


def example_15_custom_order_via_config():
    """示例15: 通过配置列表使用自定义排序"""
    print("=" * 60)
    print("示例15: 通过配置列表使用自定义排序")
    print("=" * 60)

    data = {
        '订单号': ['O001', 'O002', 'O003', 'O004', 'O005', 'O006'],
        '状态': ['已发货', '待支付', '已完成', '待发货', '已完成', '待支付'],
        '金额': [500, 200, 800, 300, 600, 150]
    }
    df = pd.DataFrame(data)
    print("原始数据:")
    print(df)
    print("\n" + "-" * 60)

    config = [
        {'column': '状态', 'ascending': True, 'order': ['待支付', '待发货', '已发货', '已完成']},
        {'column': '金额', 'ascending': False}
    ]
    sorter = MultiColumnSorter()
    result = sorter.sort_by_config(df, config)
    print("按 状态(待支付→待发货→已发货→已完成)、金额(降序) 排序结果:")
    print(result)
    print()


def example_16_custom_order_convenience_method():
    """示例16: 使用 sort_with_custom_order 便捷方法"""
    print("=" * 60)
    print("示例16: 使用 sort_with_custom_order 便捷方法")
    print("=" * 60)

    data = {
        '商品': ['手机', '电脑', '平板', '耳机', '手表', '键盘'],
        '分类': ['电子产品', '电子产品', '电子产品', '配件', '电子产品', '配件'],
        '库存等级': ['充足', '紧张', '一般', '充足', '缺货', '一般']
    }
    df = pd.DataFrame(data)
    print("原始数据:")
    print(df)
    print("\n" + "-" * 60)

    sorter = MultiColumnSorter()
    result = sorter.sort_with_custom_order(
        df,
        sort_columns=['库存等级', '分类'],
        custom_orders={
            '库存等级': ['缺货', '紧张', '一般', '充足'],
            '分类': ['电子产品', '配件']
        }
    )
    print("按 库存等级(缺货→紧张→一般→充足)、分类 排序结果:")
    print(result)
    print()


def example_17_custom_order_unknown_values():
    """示例17: 自定义排序中未定义值的处理"""
    print("=" * 60)
    print("示例17: 自定义排序 - 未定义值排在末尾")
    print("=" * 60)

    data = {
        '项目': ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7'],
        '风险等级': ['高', '中', '低', '极高', '高', '极低', '中']
    }
    df = pd.DataFrame(data)
    print("原始数据（含未定义值：极高、极低）:")
    print(df)
    print("\n" + "-" * 60)

    sorter = MultiColumnSorter()
    custom_orders = {'风险等级': ['高', '中', '低']}
    result = sorter.sort(df, sort_columns='风险等级', ascending=True, custom_orders=custom_orders)
    print("排序结果（未定义值自动排在末尾）:")
    print(result)
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
    example_8_mixed_numeric_sort()
    example_9_mixed_datetime_sort()
    example_10_multi_column_mixed_sort()
    example_11_string_numeric_lexicographic_fix()
    example_12_custom_order_basic()
    example_13_custom_order_with_other_cols()
    example_14_custom_order_multiple_cols()
    example_15_custom_order_via_config()
    example_16_custom_order_convenience_method()
    example_17_custom_order_unknown_values()


if __name__ == "__main__":
    main()
