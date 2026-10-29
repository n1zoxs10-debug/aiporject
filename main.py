import streamlit as st
st.title ('저메추 해죵')
a=st.text_input('이름 머임')
b=st.selectbox('머먹을거얌?',['한식','양식','중식','일식'])
if st.button('좋은 선택!'):
  st.write('하잉')

