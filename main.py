import streamlit as st
st.title ('저메추 해주는 사람:3')
a=st.text_input('당신의 이름은?')
b=st.selectbox('머 먹을까염?',['한식','양식','중식','일식'])
if st.button('골라골라'):
  st.write('연어 사케동!')
  st.info(a+'이! 반가웡')
  st.warning(b+'를 드세욤!')
  st.error('고맙수다')
  st.balloons()
             

