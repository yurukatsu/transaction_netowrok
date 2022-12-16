import datetime
from pathlib import Path
from typing import List

import streamlit as st
from PIL import Image

# 変数
# 作業ディレクトリ
WORKING_DIR = Path(".")
# 画像ディレクトリ
IMG_DIR = WORKING_DIR / "imgs"
# CSSディレクトリ
CSS_DIR = WORKING_DIR / "css"
# 今日の日付
TODAY = datetime.datetime.today()

def set_page_config():
    st.set_page_config(
        page_title="TRICS",
        page_icon="🌐",
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
    
def make_header():
    # タイトルロゴをインポート
    img_file = str(IMG_DIR / "project_logo.png")
    img_ = Image.open(img_file)
    # 画像を中央に配置
    cols = st.columns(3)
    cols[1].image(img_, use_column_width=True)

class Content:
    name = None
    href = None
    
    @classmethod
    def make_title(cls):
        st.write(
            f"""
            <h4>
            <a name={cls.href}>{cls.name}<a>
            </h4>
            """,
            unsafe_allow_html=True
        )
    
    @classmethod
    def make(cls):
        pass
    
class Degree(Content):
    name = "Degree"
    href = name.lower().replace(" ", "-")
    
    @classmethod
    def make(cls):
        cls.make_title()
        # 2行にする
        cols = st.columns([1, 2])
        # 左の行
        with cols[0]:
            # 説明
            with st.expander("See definition"):
                st.write(
                    """
                    The degree of a node in a network (sometimes referred to incorrectly as the connectivity) is the number of connections or edges the node has to other nodes. If a network is directed, meaning that edges point in one direction from one node to another node, then nodes have two different degrees, the in-degree, which is the number of incoming edges, and the out-degree, which is the number of outgoing edges.
                    """
                )
            # スコア表示
            avg_degree = 2.1
            st.metric(label="Avg. degree", value=2.1)
            
class ClusterCoefficient(Content):
    name = "Cluster Coefficient"
    href = name.lower().replace(" ", "-")
    
    @classmethod
    def make(cls):
        cls.make_title()
        # 2行にする
        cols = st.columns([1, 2])
        # 左の行
        with cols[0]:
            # 説明
            with st.expander("See definition"):
                st.write(
                    """
                    In graph theory, a clustering coefficient is a measure of the degree to which nodes in a graph tend to cluster together. 
                    """
                )
            # スコア表示
            avg_degree = 2.1
            st.metric(label="Avg. cluster coefficient", value=0.03)

class Body:
    def __init__(self, contents: List = None):
        self.contents = contents.copy() if contents else None
        self.date = TODAY
        
    def make(self):
        st.write(f"## TODAY'S POINTS")
        self.date = st.date_input(
            "Date",
            TODAY
        )
        
        if not self.contents is None:
            for content in self.contents:
                with st.container():
                    content.make()
                    
def make_sidebar(contents):
    sidebar = st.sidebar
    sidebar.write("# CONTENTS")
    
    if not contents is None:
        with sidebar.container():
            for content in contents:
                st.write(
                    f"""
                    <a href=#{content.href}>{content.name}<a>
                    """,
                    unsafe_allow_html=True
                )

def main():
    # ページ設定反映
    set_page_config()
    # CSS反映
    set_css()
    # APP（ページをまたいで）共有するベースデータ
    if 'df_base' not in st.session_state:
        st.session_state['df_base'] = Trics.read_pickle(TRICS_DATA_FILE)
    # ヘッダー作成
    with st.container():
        make_header()
    # コンテンツ
    contents = [Degree, ClusterCoefficient]
    # ボディ作成
    with st.container():
        body = Body(contents)
        body.make()
    # サイドバー作成
    make_sidebar(contents)

if __name__ == "__main__":
    main()