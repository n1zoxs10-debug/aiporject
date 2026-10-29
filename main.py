import streamlit as st
st.title ('저메추 해주는 사람:3')
a=st.text_input('당신의 이름은?')
b=st.selectbox('머 먹을까염?',['한식','양식','중식','일식'])
if st.button('좋은 선택!'):
  st.write('아주 좋은선택!')

