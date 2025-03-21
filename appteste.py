import streamlit as st
import cv2
import numpy as np
from PIL import Image
import pymysql
import io
import datetime

# Conexão com banco
def conectar_banco():
    return pymysql.connect(host="186.224.105.220", port=3306, user="panavarr", password="331sbA8g?", database="panavarr_", charset='utf8mb4')

# Salvar imagem no banco
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

# Ler QR Code usando OpenCV
def ler_qrcode_opencv(imagem_pil):
    imagem_cv = np.array(imagem_pil)
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(imagem_cv)
    if bbox is not None and data:
        return data
    return None

# Streamlit UI
st.title('📸 Captura Automática com Leitura de QR Code')

img_camera = st.camera_input("Capture a imagem com QR Code")

if img_camera:
    imagem_pil = Image.open(img_camera)
    st.image(imagem_pil, caption='Imagem capturada', use_container_width=True)

    nota_fiscal = ler_qrcode_opencv(imagem_pil)

    if nota_fiscal:
        st.success(f"QR Code detectado: {nota_fiscal}")

        tipo_envio = st.radio("Selecione o tipo de envio:", ["Motorista", "Transportadora"])
        nome_motorista = st.text_input("Nome do Motorista (se aplicável)", "") if tipo_envio == "Motorista" else "Transportadora"

        if st.button("Salvar imagem e Nota Fiscal"):
            salvar_imagem_no_banco(imagem_pil, nota_fiscal, nome_motorista)
            st.success("Imagem e Nota Fiscal salvas com sucesso!")

    else:
        st.error("Nenhum QR Code detectado. Tente novamente com uma imagem mais clara.")