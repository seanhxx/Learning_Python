from pyspark import SparkContext
from pyspark.sql import HiveContext, DataFrame, Column, Window, DataFrameWriter
from pyspark.sql.functions import rank, col
from datetime import timedelta, datetime
import pytz
import os

sc = SparkContext()
hc = HiveContext(sc)
# table 1
table_lot_history = hc.table("prod_mti_ww_be_idl.tte_2did_lot_history_view")
table_lot_history.registerTempTable("table_lot_history")
# table 2
table_machine_attr = hc.table("prod_mti_ww_be_idl.tte_2did_machine_attr_view")
table_machine_attr.registerTempTable("table_machine_attr")
# table 3
table_lot_relation = hc.table("prod_mti_ww_be_idl.tte_2did_lot_relation_view")
table_lot_relation.registerTempTable("table_lot_relation")
# table 4
table_comp_history = hc.table("prod_mti_ww_be_idl.tte_2did_comp_history_view")
table_comp_history.registerTempTable("table_comp_history")

ctz = pytz.timezone('Singapore')
path_root = '/eng/mti/ww/be/msb/assembly_quality/twodid'

for n in range(1, 2):
    date = (datetime.now(tz=ctz) - timedelta(days=n)).strftime("%Y-%m-%d")
    for t in (1, 2):
        if t == 1:
            time_boundary_1 = date + ' ' + '00:00:00.000'
            time_boundary_2 = date + ' ' + '11:59:59.999'
            file_path = os.path.join(path_root, date + '_a')
        else:
            time_boundary_1 = date + ' ' + '12:00:00.000'
            time_boundary_2 = date + ' ' + '23:59:59.999'
            file_path = os.path.join(path_root, date + '_b')

        # query on table 1 to get completed lot
        query_1_a = "SELECT site, slash_lot_id, design_id FROM table_lot_history \
                     WHERE site = 'MSB' AND step = 'O/S TEST' \
                     AND start_datetime BETWEEN '%s' AND '%s'" % (time_boundary_1, time_boundary_2)
        df1_a = hc.sql(query_1_a)

        # table 1 to get all steps and time ranking
        query_1_b = "SELECT slash_lot_id, step, start_datetime FROM table_lot_history WHERE site = 'MSB'"
        df1_b = hc.sql(query_1_b)
        df1 = df1_a.join(df1_b, df1_a['slash_lot_id'] == df1_b['slash_lot_id'], 'inner') \
            .select('site', 'design_id', df1_a['slash_lot_id'], 'step', 'start_datetime').distinct()
        df1_window = Window.partitionBy(df1['slash_lot_id'], df1['step']).orderBy(df1['start_datetime'].desc())
        df1_rank = df1.select('*', rank().over(df1_window).alias('rank')).filter("rank = 1")

        # table 2 get attr such as strip id...
        query_2 = "SELECT slash_lot_id, machine_id, step, strip_id, strip_datetime \
                   FROM table_machine_attr WHERE site = 'MSB'"
        df2 = hc.sql(query_2)

        # merge lot id, steps, strip id...
        cond_df3_a = [df2["slash_lot_id"] == df1_rank["slash_lot_id"], df2["step"] == df1_rank["step"]]
        df3_a = df2.join(df1_rank, cond_df3_a, 'inner') \
            .select('site', 'design_id', df1_rank['slash_lot_id'], 'strip_id', df1_rank['step'],
                    'machine_id', 'start_datetime', 'strip_datetime').distinct()

        # add strip id to 'O/S test' row
        df3_b = df3_a.select('slash_lot_id', 'strip_id').distinct()
        df3_c = df3_a.select('site', 'design_id', 'slash_lot_id', 'step', 'machine_id', 'start_datetime') \
            .filter("step = 'O/S TEST'").distinct()
        df3_d = df3_c.join(df3_b, df3_c['slash_lot_id'] == df3_b['slash_lot_id'], 'inner') \
            .select('site', 'design_id', df3_c['slash_lot_id'], 'strip_id', 'step',
                    'machine_id', 'start_datetime', col('start_datetime').alias('strip_datetime')).distinct()
        df3_e = df3_a.unionAll(df3_d).dropna(how='any')

        # find relation between lot_id and 2did
        query_4 = "SELECT slash_lot_id, 2did, comp_datetime FROM table_lot_relation WHERE site = 'MSB'"
        df4 = hc.sql(query_4)

        df4_a = df3_e.join(df4, df3_e['slash_lot_id'] == df4['slash_lot_id'], 'inner')\
            .select('site', 'design_id', df3_e['slash_lot_id'], 'strip_id', '2did', 'step',
                    'machine_id', 'start_datetime', 'strip_datetime', 'comp_datetime')

        # find fuse id
        query_5 = "SELECT 2did, fuseid FROM table_comp_history WHERE site = 'MSB'"
        df5 = hc.sql(query_5).dropna(how='any')
        df6 = df4_a.join(df5, df5["2did"] == df4_a["2did"], 'inner') \
            .select('site', 'design_id', 'slash_lot_id', 'strip_id', df5['2did'], 'fuseid', 'step',
                    'machine_id', col('start_datetime').alias('process_datetime'), 'strip_datetime',
                    'comp_datetime').distinct()

        df6.write.parquet(file_path)

        # df = hc.read.parquet('/eng/mti/ww/be/msb/assembly_quality/twodid/2017-05-08_a/*.parquet')
        # filepath = os.path.join("/home/hdfsbe/auto-diagnostics", 'sample_z.csv')
        # df.toPandas().to_csv(filepath)
