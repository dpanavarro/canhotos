import streamlit as st
from PIL import Image
import io
import datetime
import pymysql
from pyzbar.pyzbar import decode

# Função para conectar ao banco de dados
def conectar_banco():
    return pymysql.connect(
            host="186.224.105.220",
            port=3306,
            user="panavarr",
            password="331sbA8g?",
            database="panavarr_",
            charset='utf8mb4'
            )

# Função para salvar a imagem no banco
def salvar_imagem_no_banco(imagem, nota_fiscal, info_envio):
    conn = conectar_banco()
    cursor = conn.cursor()

    if imagem.mode == 'RGBA':
        imagem = imagem.convert('RGB')

    img_byte_arr = io.BytesIO()
    imagem.save(img_byte_arr, format='JPEG')
    imagem_binaria = img_byte_arr.getvalue()

    data_atual = datetime.datetime.now()

    cursor.execute("""
        INSERT INTO notafiscaiscanhotosjrp (NumeroNota, DataBipe, CaminhoImagem, Imagem, InfoEnvio)
        VALUES (%s, %s, %s, %s, %s)
        """, (nota_fiscal, data_atual, "caminho_fake.jpg", imagem_binaria, info_envio))

    conn.commit()
    cursor.close()
    conn.close()

# Função para ler código de barras da imagem usando pyzbar
def ler_codigo_barras(imagem):
    decoded_objects = decode(imagem)
    for obj in decoded_objects:
        return obj.data.decode('utf-8')
    return None

# Página Streamlit
st.title('📸 Captura Automática por Código de Barras')

img_camera = st.camera_input("Capture a imagem com o código de barras")

if img_camera:
    imagem_pil = Image.open(img_camera)
    st.image(imagem_pil, caption='Imagem capturada', use_container_width=True)

    nota_fiscal = ler_codigo_barras(imagem_pil)

    if nota_fiscal:
        st.success(f"Código de barras detectado: {nota_fiscal}")

        tipo_envio = st.radio("Selecione o tipo de envio:", ["Motorista", "Transportadora"])
        nome_motorista = st.text_input("Nome do Motorista (se aplicável)", "") if tipo_envio == "Motorista" else "Transportadora"

        if st.button("Salvar imagem e Nota Fiscal"):
            salvar_imagem_no_banco(imagem_pil, nota_fiscal, nome_motorista)
            st.success("Imagem e Nota Fiscal salvas com sucesso!")

    else:
        st.error("Nenhum código de barras detectado. Tente novamente.")
