import datetime
import sys
import time
from pathlib import Path
from typing import List, Tuple, Dict

import networkx as nx
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
from pyvis.network  import Network
# 自作パッケージ
from utils.data import Trics

# 変数
# 作業ディレクトリ
WORKING_DIR = Path(".")
# 画像ディレクトリ
IMG_DIR = WORKING_DIR / "imgs"
# CSSディレクトリ
CSS_DIR = WORKING_DIR / "css"
# データディレクトリ
DATA_DIR = WORKING_DIR / "data" / "interim"
# HTMLディレクトリ
HTML_DIR = WORKING_DIR / "html"
# TRICSデータ
TRICS_DATA_FILE = DATA_DIR / "trics_rm.pkl"
# 今日の日付
# TODAY = datetime.datetime.today()
TODAY = datetime.datetime(2022, 4, 28) # デバッグ用

def set_page_config():
    st.set_page_config(
        page_title="ANALYSIS",
        page_icon="🕸️",
        layout="wide",
        initial_sidebar_state="auto"
    )
    
def set_css():
    # cssファイル
    file = CSS_DIR / "style.css"
    # ファイル開く
    with file.open("r") as f:
        css_text = f.read()
    # 反映
    st.write(
        f"<style>{css_text}</style>",
        unsafe_allow_html=True
    )
    
class Header:
    @classmethod
    def make(cls, company:str, start_date:datetime.datetime, end_date:datetime.datetime):
        with st.container():
            start_date_str = start_date.strftime("%Y/%m/%d")
            end_date_str = end_date.strftime("%Y/%m/%d")
            st.write(f"# {company} ({start_date_str} - {end_date_str})")
            cls.show_page_description()
            
        
    @classmethod
    def show_page_description(cls):
        text = r"""
            This page shows the results of the network analysis for a particular company. To create the network, transactions from a firm X to a firm Y during the specified sample period are combined (e.g., if transactions of \$200 and \$100 in value are made from X to Y in April 2022, the link feature from X to Y is \$300).
            """
        with st.expander("About this page"):
            st.write(text)

class Setting:
    @classmethod
    def input_company(cls):
        company = st.text_input("Company", value="MIZUHO BANK", help="Input a company name")
        return company
    
    @classmethod
    def select_date(cls) -> Tuple[datetime.datetime, datetime.datetime]:
        cols = st.columns(2)
        with cols[0]:
            date_ = st.date_input(
                "Start",
                TODAY,
                help="Select start date"
            )
            start_date = datetime.datetime(date_.year, date_.month, date_.day)
        with cols[1]:
            date_ = st.date_input(
                "End",
                TODAY,
                help="Select end date"
            )
            end_date = datetime.datetime(date_.year, date_.month, date_.day)
        return start_date, end_date
    
    @classmethod
    def input_amount_conditions(cls) -> Tuple[int, int]:
        cols = st.columns(2)
        with cols[0]:
            max_amount = st.number_input(
                "Maximum of deal maounts",
                value=10**7,
                help="Inpu maximum of deal amounts"
                )
        with cols[1]:
            min_amount = st.number_input(
                "Minimum of deal maounts",
                value=0,
                help="Inpu minimum of deal amounts"
                )
        return max_amount, min_amount
    
class DataFrame:
    @classmethod
    # @st.cache
    def update(
        cls,
        df: pd.DataFrame,
        date_col: str,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        amount_col: str,
        max_amount: int,
        min_amount: int
    ):
        df = Trics.filter_data_by_date(df, "VALUE_DATE", start_date, end_date)
        df = Trics.filter_data_by_amount(df, "AMOUNT_USD", max_amount, min_amount)
        return df
    
class Sidebar(Setting, DataFrame):
    def __init__(self):
        self.sidebar = st.sidebar
        
    def make_header(self):
        # タイトルロゴをインポート
        img_file = str(IMG_DIR / "project_logo.png")
        img_ = Image.open(img_file)
        # 画像を中央に配置（and サイズ調整）
        cols = self.sidebar.columns([1,3,1])
        cols[1].image(img_, use_column_width=True)
        
    def make_content_list(self, content_catalog: List):
        # コンテンツ表示
        self.sidebar.write("# CONTENTS")
        # コンテンツ一覧
        if not content_catalog is None:
            with self.sidebar.container():
                for content in content_catalog:
                    _content = content["content"]
                    st.write(
                        f"""
                        <a href=#{_content.href}>{_content.name}<a>
                        """,
                        unsafe_allow_html=True
                    )
    
    def aleart_initial_setting(self):
        with self.sidebar.container():
            st.warning("At first,input settings and update data!")
    
    def set_company(self, company_list: List[str], show_setting_title:bool = False):
        if show_setting_title:
            # コンテンツ表示
            self.sidebar.write("# SETTINGS")
        with self.sidebar.container():
            company = self.input_company()
            if company not in company_list:
                st.error(f"{company} dosen't exist!")
        return company
    
    def set_date(self, show_setting_title:bool = False) -> Tuple[datetime.datetime, datetime.datetime]:
        if show_setting_title:
            # コンテンツ表示
            self.sidebar.write("# SETTINGS")
        with self.sidebar.container():
            start_date, end_date = self.select_date()
            if start_date > end_date:
                st.warning("Start date later than end date!!!")
        return start_date, end_date
    
    def set_amount_conditions(self, show_setting_title:bool = False):
        if show_setting_title:
            # コンテンツ表示
            self.sidebar.write("# SETTINGS")
        with self.sidebar.container():
            max_amount, min_amount = self.input_amount_conditions()
            if max_amount < min_amount:
                st.warning("Minimum grater than maximum!!!")
        return max_amount, min_amount
    
    def update_dataframe(
        self,
        df: pd.DataFrame,
        date_col: str,
        start_date: datetime.datetime,
        end_date: datetime.datetime,
        amount_col: str,
        max_amount: int,
        min_amount: int,
        is_updated_before: bool
        ):
        with self.sidebar.container():
            bt = st.button("Update", type="primary", disabled=False)
            if bt:
                df = self.update(df, date_col, start_date, end_date, amount_col, max_amount, min_amount)            
                success_message = st.success('Data is update!', icon="✅")
                time.sleep(1)
                success_message.empty()
                is_updated_before = True
        return df, is_updated_before

class Body:
    def __init__(self, content_catalog: List[Dict]):
        self.content_catalog = content_catalog.copy() if content_catalog else None
        
    def make(self):
        if not self.content_catalog is None:
            for content in self.content_catalog:
                _content = content["content"]
                args = content["args"].copy()
                kwargs = content["kwargs"].copy()
                with st.container():
                    content_instance = _content(*args, **kwargs)
                    content_instance.make()
                    
class Content:
    name = None
    href = None
    
    def ___init__(self):
        pass
    
    def make_title(self):
        st.write(
            f"""
            <h2>
            <a name={self.href}>{self.name}<a>
            </h2>
            """,
            unsafe_allow_html=True
        )
    
    def make(self):
        pass
    
class NetworkVisualization(Content):
    name = "Network Diagram"
    href = name.lower().replace(" ", "-")
    
    def __init__(self, message, hoge: str = "hoge"):
        self.message = message
        self.hoge = hoge
    
    def make(self):
        with st.container():
            self.make_title()
            st.write(f"Diagram is here. {self.message}, {self.hoge}")

def main():
    # 列名
    SOURCE = "REMITTER_ENGLISH"
    TARGET = "BENEFICIARY_ENGLISH"
    DATE_COL = "VALUE_DATE"
    AMOUNT_COL = "AMOUNT_USD"
    
    # ページ設定反映
    set_page_config()
    
    # CSS反映
    set_css()
    
    # APP（ページをまたいで）共有するベースデータ
    if 'df_base' not in st.session_state:
        st.session_state.df_base = Trics.read_pickle(TRICS_DATA_FILE)
    
    # コンテンツ
    content_catalog = [
        {
            "content": NetworkVisualization,
            "args": ["Hellooooooooo"],
            "kwargs": {"hoge": "hgoeeeeee"}
        },
    ]
    
    # サイドバー作成
    sidebar = Sidebar()
    sidebar.make_header()
    # 設定
    # 最初にアップデートしたか判断する
    if 'is_updated_before' not in st.session_state:
        sidebar.aleart_initial_setting()
        st.session_state.is_updated_before = False
    # 会社名の入力
    # 会社候補
    company_list = Trics().create_company_list(
        st.session_state.df_base,
        SOURCE,
        TARGET
        )
    company = sidebar.set_company(company_list, show_setting_title=True)
    # データサンプル期間
    start_date, end_date = sidebar.set_date()
    # 取引量
    max_amount, min_amount = sidebar.set_amount_conditions()
    # 使用データのアプデート
    df, st.session_state.is_updated_before = sidebar.update_dataframe(
        st.session_state.df_base,
        DATE_COL,
        start_date,
        end_date,
        AMOUNT_COL,
        max_amount,
        min_amount,
        st.session_state.is_updated_before
        )
    # コンテンツ一覧表示
    sidebar.make_content_list(content_catalog)
    
    # グラフ作成
    # MG = Trics.create_MultiDiGraph(
    #     df,
    #     source='REMITTER_ENGLISH',
    #     target='BENEFICIARY_ENGLISH',
    #     edge_attr=["AMOUNT_USD", "VALUE_DATE"],
    #     )
    
    # データがアップデートされたら
    if st.session_state.is_updated_before:
        # ヘッダー表示
        Header.make(company, start_date, end_date)
        st.write(f"{len(df)}")
        body = Body(content_catalog)
        body.make()
        
        df[DATE_COL] = df[DATE_COL].dt.strftime("%Y%m%d")
        G = Trics().create_MultiDiGraph(df, SOURCE, TARGET, [DATE_COL, AMOUNT_COL])
        singleG = nx.DiGraph(G)
        subsingleG = nx.ego_graph(singleG, company, radius=2, center=True, undirected=False)
        subG = nx.subgraph(G, subsingleG)
        d = dict(G.degree)
        node_scale = 10
        buffer = 5
        d.update((x, node_scale*np.tanh(y/10) + buffer) for x, y in d.items())
        nx.set_node_attributes(G, d, 'size')
        
        g = Network(
            height='700px',
            width='700px',
            directed=True,
            notebook=False,
            bgcolor='#101035',
            font_color='#ffffff',
            neighborhood_highlight=False,
            select_menu=False
        )
        g.from_nx(subG)
        for node in g.nodes:
            if node['id'] == company:
                node['color'] = "#AA4309"
            else:
                node['color'] = '#97c2fc'
            node["title"] = f"""Company: {node["id"]}\nDegree (in the subgraph): {node["size"]}"""
                
        amount_max = 0
        scale = 5.0
        base=0.5 
        for edge in g.edges:
            amount_max = edge[AMOUNT_COL] if amount_max < edge[AMOUNT_COL] else amount_max
                
        for edge in g.edges:
            edge["width"] = edge[AMOUNT_COL] * scale / amount_max + base
            edge["title"] = f"""Deal amount: {edge[AMOUNT_COL]} USD\nDate: {edge[DATE_COL]}"""
    
        tmp_file = HTML_DIR / ".tmp" / "network_vis.html"
        g.show(str(tmp_file))
        
        with tmp_file.open(mode='r', encoding='utf-8') as f:
            source_code = f.read()
        st.components.v1.html(source_code, height=710, width=702)
        
        
        
if __name__ == "__main__":
    main()