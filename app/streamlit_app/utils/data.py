"""
データ取得やネットワーク作成に関するもの
"""
import datetime
from pathlib import Path
from typing import List

import networkx as nx
import pandas as pd
import streamlit as st


class Trics():
    column_list: List[str] = [
        'COUNTRY_FROM',
        'COUNTRY_TO',
        'REMITTING_BANK_BIC',
        'BENEFICIARY_BANK_BIC',
        'REMITTER_ENGLISH', # 企業名（仕向）
        'BENEFICIARY_ENGLISH', # 企業名（非仕向）
        'VALUE_DATE', # 取引処理日
        'CURRENCY',
        'AMOUNT',
        'AMOUNT_USD', # 金額（＄）
        'DETAILS',
        'DIRECTION',
        'REMITTER_M_CIF',
        'REMITTER_PARENT_COMPANY2',
        'REMITTER_PARENT_M_CIF',
        'BENEFICIARY_M_CIF',
        'BENEFICIARY_PARENT_COMPANY2',
        'BENEFICIARY_PARENT_M_CIF',
        'ORDERING_COUNTRY_FROM',
        'ACCOUNT_COUNTRY_TO'
        ]
    usecols: List[str] = [
        'COUNTRY_FROM',
        'COUNTRY_TO',
        'REMITTING_BANK_BIC',
        'BENEFICIARY_BANK_BIC',
        'REMITTER_ENGLISH', # 企業名（仕向）
        'BENEFICIARY_ENGLISH', # 企業名（非仕向）
        'VALUE_DATE', # 取引処理日
        'CURRENCY',
        'AMOUNT_USD', # 金額（＄）
        'DETAILS',
        'DIRECTION'
        ]
    
    @classmethod
    @st.cache(allow_output_mutation=True)
    def read_pickle(cls, data_path: Path, usecols: List[str] = None) -> pd.DataFrame:
        df = pd.read_pickle(data_path)
        if usecols is None:
            usecols = cls.usecols.copy()
        df = df.loc[:, usecols]
        return df
    
    @classmethod
    # @st.cache
    def filter_data_by_date(
        cls, 
        df: pd.DataFrame,
        date_col: str,
        start_date: datetime.datetime,
        end_date: datetime.datetime
        ) -> pd.DataFrame():
        df[date_col] = pd.to_datetime(df[date_col])
        mask_ = (df[date_col] >= start_date) & (df[date_col] <= end_date)
        df = df[mask_].copy()
        return df
    
    @classmethod
    # @st.cache
    def filter_data_by_amount(
        cls, 
        df: pd.DataFrame,
        amount_col: str,
        max_amount: datetime.datetime,
        min_amount: datetime.datetime
        ) -> pd.DataFrame():
        mask_ = (df[amount_col] >= min_amount) & (df[amount_col] <= max_amount)
        df = df[mask_].copy()
        return df
    
    @classmethod
    @st.cache
    def create_company_list(
        cls,
        df: pd.DataFrame,
        remitter_col: str,
        beneficiary_col: str
        ) -> List[str]:
        
        companies = df.loc[:, remitter_col].unique().tolist()
        companies.extend(
            df.loc[:, beneficiary_col].unique().tolist()
            )
        return list(set(companies))
        
    @classmethod
    # @st.cache(allow_output_mutation=True)
    def create_MultiDiGraph(
        cls,
        df,
        source,
        target,
        edge_attr,
        edge_keys=None
        ) -> nx.MultiDiGraph:
        MG = nx.from_pandas_edgelist(
            df,
            source=source,
            target=target,
            edge_attr=edge_attr,
            create_using=nx.MultiDiGraph,
            edge_key=edge_keys
            )
        return MG