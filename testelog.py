import streamlit as st
import cv2
import numpy as np
import plotly.graph_objects as go

import os
from PIL import Image
import io  
import base64

import mysql.connector
from mysql.connector import Error


# Função para calcular a similaridade usando ORB
def orb_sim(img1, img2):
    orb = cv2.ORB_create()
    kp_a, desc_a = orb.detectAndCompute(img1, None)
    kp_b, desc_b = orb.detectAndCompute(img2, None)
    if desc_a is None or desc_b is None:
        return None
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(desc_a, desc_b)
    similar_regions = [i for i in matches if i.distance < 50]
    if len(matches) == 0:
        return 0
    return len(similar_regions) / len(matches)

# Função para carregar uma imagem a partir de um arquivo
def load_image(uploaded_file):
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    return cv2.imdecode(file_bytes, 0)

# Função para configurar a navegação
def navigate(page):
    st.session_state["page"] = page

# Inicializando o estado de sessão
if "page" not in st.session_state:
    st.session_state["page"] = "welcome"
if "images_reference" not in st.session_state:
    st.session_state["images_reference"] = []
if "images_consent" not in st.session_state:
    st.session_state["images_consent"] = []
if "cadastro" not in st.session_state:
    st.session_state["cadastro"] = {"completed": False}

# Adicionar CSS para estilizar a aplicação
with open("styles.css") as f:
    st.markdown (f"<style>{f.read()}</style>", unsafe_allow_html=True)

def add_custom_css():
    st.markdown("""
<style>
           body, html, [data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #050027, #0F006E);
    color: white;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0;
    padding: 0;
    font-family: 'Arial', sans-serif;
}

.container {
    text-align: center;
    width: 100%;
}

.logo {
    display: block;
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 40px;
    width: 400px;
}
        </style>
    """, unsafe_allow_html=True)

def welcome_page():
    add_custom_css()  # Adiciona o CSS customizado
    st.markdown("<div class='container'><img src='data:image/png;base64,{}' class='logo' /></div>".format(image_base64), unsafe_allow_html=True)
    
    # Criar três colunas
    col1, col2, col3 = st.columns([1.5, 1.5, 1.5])
    
    # Deixar as colunas laterais vazias
    col1.write("")
    col3.write("")
    
    # Colocar os botões na coluna central
    with col2:
        st.markdown("<style>div.stButton > button:first-child {width: 200px;}</style>", unsafe_allow_html=True)
        st.button("Cadastrar", on_click=navigate, args=("register",))
        st.button("Login", on_click=navigate, args=("login",))

# Transformar imagem para base64
import base64
from PIL import Image

def get_image_as_base64(image_path):
    img = Image.open(image_path)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

image_path = "LOGO_BRANCA-removebg-preview.png"
image_base64 = get_image_as_base64(image_path)


# Página de cadastro
def add_custom_css2():
    st.markdown("""
        <style>
           body, html, [data-testid="stAppViewContainer"] {
               background: #050027;
           }
        </style>
    """, unsafe_allow_html=True)

# Função para conexão com o banco de dados MySQL
def conectar_bd():
    try:
        conexao = mysql.connector.connect(
            host='localhost',
            database='db_ava',
            user='root',
            password='nova_senha'
        )
        return conexao
    except mysql.connector.Error as err:
        st.error(f"Erro ao conectar ao banco de dados: {err}")
        return None

# Função para inserir os dados no banco de dados
def inserir_usuario_endereco(senha, rua, bairro, cep, numero, cidade):
    conexao = conectar_bd()
    if conexao:
        cursor = conexao.cursor()
        try:
            declaracao = """INSERT INTO usuario_endereco (senha, rua, bairro_, cep, numero, cidade) 
                            VALUES (%s, %s, %s, %s, %s, %s)"""
            dados = (senha, rua, bairro, cep, numero, cidade)
            cursor.execute(declaracao, dados)
            conexao.commit()
            st.success("Cadastro realizado com sucesso e salvo no banco de dados!")
        except mysql.connector.Error as err:
            st.error(f"Erro ao inserir dados: {err}")
        finally:
            cursor.close()
            conexao.close()

# Função de registro da página
def register_page():
    add_custom_css2()  
    st.markdown("# CADASTRAR")

    with st.form(key="register_form"):

        institution_name = st.text_input("Nome da instituição")
        rua = st.text_input("Rua")
        bairro = st.text_input("Bairro")
        numero = st.text_input("Número")
        cep = st.text_input("CEP")
        cidade = st.text_input("Cidade")
        telefone = st.text_input("Telefone")
        password = st.text_input("Senha", type="password")
        confirm_password = st.text_input("Confirme a senha", type="password")

        submit_button = st.form_submit_button(label="Cadastrar")

    if submit_button:
        if password == confirm_password:
            st.success("Cadastro realizado com sucesso!")

            if "cadastro" not in st.session_state:
                st.session_state["cadastro"] = {}

            st.session_state["cadastro"]["completed"] = True
            st.session_state["cadastro"]["nome"] = institution_name
            st.session_state["cadastro"]["rua"] = rua
            st.session_state["cadastro"]["bairro"] = bairro
            st.session_state["cadastro"]["numero"] = numero
            st.session_state["cadastro"]["cep"] = cep
            st.session_state["cadastro"]["cidade"] = cidade
            st.session_state["cadastro"]["telefone"] = telefone
            inserir_usuario_endereco(password, rua, bairro, cep, numero, cidade)
        else:
            st.error("As senhas não coincidem. Tente novamente.")
    st.button("Voltar", on_click=navigate, args=("welcome",))

def add_custom_css3():
    st.markdown("""
<style>
           body, html, [data-testid="stAppViewContainer"] {
    background: #050027;
}
        </style>
    """, unsafe_allow_html=True)
# Página de login
def login_page():
    add_custom_css3()
    st.markdown("# LOGIN")
    username = st.text_input("Nome do usuário")
    password = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        st.success("Login realizado com sucesso!")
        navigate("home")
    st.button("Voltar", on_click=navigate, args=("welcome",))

def add_custom_css4():
    st.markdown("""
    <style>
        /* Estilização geral da página */
        body, html, [data-testid="stAppViewContainer"] {
            background-color: #050027;
            color: white;
            font-family: 'Arial', sans-serif;
        }

        /* Estilização específica para os botões nesta página */
        div.stButton > button {
            background-color: #1D1454  !important;  /* Cor de fundo dos botões */
            border: 2px solid white !important;    /* Borda branca ao redor dos botões */
            color: white !important;               /* Cor do texto dos botões */
            border-radius: 12px !important;        /* Bordas arredondadas */
            font-size: 18px !important;            /* Tamanho da fonte */
            padding: 10px 20px !important;         /* Espaçamento interno */
            margin-top: 10px !important;           /* Espaçamento superior */
            width: 100% !important;                /* Largura dos botões */
            box-shadow: none !important;           /* Remove a sombra padrão */
        }

        /* Remove a mudança de cor ao passar o mouse */
        div.stButton > button:hover {
            background-color: #050027 !important;
            color: white !important;
        }

        /* Remove a mudança de cor ao clicar */
        div.stButton > button:active, div.stButton > button:focus {
            background-color: #050027 !important;
            color: white !important;
        }

        /* Estilização do título */
        h1 {
            font-size: 40px;
            font-weight: bold;
            color: white;
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)
def home_page():
    add_custom_css4()
    st.button("Adicionar imagem de referência", on_click=navigate, args=("upload_reference",))
    st.button("Adicionar imagem de termo de consentimento", on_click=navigate, args=("upload_consent",))
    st.button("Adicionar imagem para verificação", on_click=navigate, args=("upload_verification",))
    st.button("Imagens de Referência", on_click=navigate, args=("registered_images_reference",))
    st.button("Imagens de Termo de Consentimento", on_click=navigate, args=("registered_images_consent",))
    st.button("Perfil do Usuário", on_click=navigate, args=("user_profile",))
    st.button("Voltar", on_click=navigate, args=("welcome",))

def add_custom_css5():
    st.markdown("""
<style>
           body, html, [data-testid="stAppViewContainer"] {
    background: #050027;
}
        </style>
    """, unsafe_allow_html=True)
# Página de cadastro de imagem de referência
def upload_reference_page():
    add_custom_css5()
    st.markdown("# CADASTRAR IMAGEM DE REFERÊNCIA")
  
    st.session_state["cadastro"]["nome"] = st.text_input("Nome")
    st.session_state["cadastro"]["rua"] = st.text_input("Rua")
    st.session_state["cadastro"]["bairro"] = st.text_input("Bairro")
    st.session_state["cadastro"]["numero"] = st.text_input("Número")
    st.session_state["cadastro"]["cep"] = st.text_input("CEP")
    st.session_state["cadastro"]["cidade"] = st.text_input("Cidade")
    st.session_state["cadastro"]["telefone"] = st.text_input("Telefone")
    st.session_state["cadastro"]["cpf"] = st.text_input("CPF")
    
    uploaded_files = st.file_uploader("Faça upload das imagens de referência", accept_multiple_files=True)
    
    if st.button("Cadastrar Imagens"):
        if not st.session_state["cadastro"]["nome"]:
            st.error("Por favor, insira o nome.")
        
        else:
            for uploaded_file in uploaded_files:
                img = load_image(uploaded_file)
                st.session_state["images_reference"].append({
                    "name": st.session_state["cadastro"]["nome"],
                    "rua": st.session_state["cadastro"]["rua"],
                    "bairro": st.session_state["cadastro"]["bairro"],
                    "numero": st.session_state["cadastro"]["numero"],
                    "cep": st.session_state["cadastro"]["cep"],
                    "cidade": st.session_state["cadastro"]["cidade"],
                    "telefone": st.session_state["cadastro"]["telefone"],
                    "cpf": st.session_state["cadastro"]["cpf"],
                    "file": img
                })
            st.success("Imagens cadastradas com sucesso!")
            st.rerun()
    st.button("Voltar", on_click=navigate, args=("home",))


def add_custom_css6():
    st.markdown("""
<style>
           body, html, [data-testid="stAppViewContainer"] {
    background: #050027;
}
        </style>
    """, unsafe_allow_html=True)
# Página de cadastro de termo de consentimento
def upload_consent_page():
    add_custom_css6()
    st.markdown("# CADASTRAR IMAGEM DE TERMO DE CONSENTIMENTO")
    image_name = st.text_input("Nome da imagem")
    uploaded_file = st.file_uploader("Faça upload")
    if st.button("Cadastrar Imagem"):
        if not image_name:
            st.error("Por favor, insira um nome para a imagem.")
        elif not uploaded_file:
            st.error("Por favor, faça o upload de uma imagem.")
        else:
            img = load_image(uploaded_file)
            st.session_state["images_consent"].append({"name": image_name, "file": img})
            st.success("Imagem de termo de consentimento cadastrada com sucesso!")
    st.button("Voltar", on_click=navigate, args=("home",))

# Função para excluir imagem
def delete_image(image_list, image_name):
    for img in image_list:
        if img["name"] == image_name:
            image_list.remove(img)
            return True
    return False

def add_custom_css7():
    st.markdown("""
<style>
           body, html, [data-testid="stAppViewContainer"] {
    background: #050027;
}
        </style>
    """, unsafe_allow_html=True)
# Página de imagens cadastradas de referência
def registered_images_reference_page():
    add_custom_css7()
    st.markdown("# IMAGENS DE REFERÊNCIA CADASTRADAS")
    
    search_query = st.text_input("Pesquise aqui...")
    filtered_images = [img for img in st.session_state["images_reference"] if search_query.lower() in img["name"].lower()]
    
    if filtered_images:
        for img in filtered_images:
            st.image(img["file"], caption=img["name"])

            if f"confirm_delete_{img['name']}" not in st.session_state:
                st.session_state[f"confirm_delete_{img['name']}"] = False

            if not st.session_state[f"confirm_delete_{img['name']}"]:
                if st.button(f"Excluir {img['name']}", key=f"delete_{img['name']}"):
                    st.session_state[f"confirm_delete_{img['name']}"] = True
            else:
                st.warning(f"Tem certeza que deseja excluir a imagem '{img['name']}'?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Sim", key=f"confirm_{img['name']}"):
                        if delete_image(st.session_state["images_reference"], img["name"]):
                            st.success(f"Imagem '{img['name']}' excluída com sucesso!")
                            st.session_state[f"confirm_delete_{img['name']}"] = False
                            st.rerun()
                with col2:
                    if st.button("Não", key=f"cancel_{img['name']}"):
                        st.session_state[f"confirm_delete_{img['name']}"] = False

    else:
        st.write("Nenhuma imagem de referência encontrada.")
    st.button("Voltar", on_click=navigate, args=("home",))


def add_custom_css8():
    st.markdown("""
<style>
           body, html, [data-testid="stAppViewContainer"] {
    background: #050027;
}
        </style>
    """, unsafe_allow_html=True)
# Página de imagens cadastradas de termo de consentimento
def registered_images_consent_page():
    add_custom_css7()
    st.markdown("# IMAGENS DE TERMO DE CONSENTIMENTO CADASTRADAS")
    
    search_query = st.text_input("Pesquise aqui...")
    filtered_images = [img for img in st.session_state["images_consent"] if search_query.lower() in img["name"].lower()]
    
    if filtered_images:
        for img in filtered_images:
            st.image(img["file"], caption=img["name"])
            
            if f"confirm_delete_{img['name']}" not in st.session_state:
                st.session_state[f"confirm_delete_{img['name']}"] = False

            if not st.session_state[f"confirm_delete_{img['name']}"]:
                if st.button(f"Excluir {img['name']}", key=f"delete_{img['name']}"):
                    st.session_state[f"confirm_delete_{img['name']}"] = True
            else:
                st.warning(f"Tem certeza que deseja excluir o termo de consentimento '{img['name']}'?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Sim", key=f"confirm_{img['name']}"):
                        if delete_image(st.session_state["images_consent"], img["name"]):
                            st.success(f"Termo de consentimento '{img['name']}' excluído com sucesso!")
                            st.session_state[f"confirm_delete_{img['name']}"] = False
                            st.rerun()
                with col2:
                    if st.button("Não", key=f"cancel_{img['name']}"):
                        st.session_state[f"confirm_delete_{img['name']}"] = False
    else:
        st.write("Nenhum termo de consentimento encontrado.")
    st.button("Voltar", on_click=navigate, args=("home",))


def add_custom_css9():
    st.markdown("""
<style>
           body, html, [data-testid="stAppViewContainer"] {
    background: #050027;
}
        </style>
    """, unsafe_allow_html=True)
# Página para upload e verificação de imagem
def upload_verification_page():
    add_custom_css9()
    st.markdown("# ADICIONAR IMAGEM PARA VERIFICAÇÃO")
    uploaded_file = st.file_uploader("Faça upload da imagem para verificação")
    if uploaded_file:
        verification_img = load_image(uploaded_file)
        st.image(verification_img, caption="Imagem para verificação")
        
        st.markdown("## Escolher Imagem de Referência")
        reference_options = [img["name"] for img in st.session_state["images_reference"]]
        selected_reference = st.selectbox("Selecione uma referência", reference_options)

        if st.button("Verificar"):
            reference_img = next(img["file"] for img in st.session_state["images_reference"] if img["name"] == selected_reference)
            similarity = orb_sim(verification_img, reference_img)
            if similarity is None:
                st.error("Não foi possível calcular a similaridade. Tente outra imagem.")
            else:
                st.write(f"Similaridade calculada: {similarity:.2f}")

                # Adiciona a lógica para calcular os valores para o gráfico
                labels = ['Similaridade', 'Diferença']
                values = [similarity * 100, 100 - (similarity * 100)]
                fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
                st.plotly_chart(fig)

    st.button("Voltar", on_click=navigate, args=("home",))

def add_custom_css10():
    st.markdown("""
<style>
           body, html, [data-testid="stAppViewContainer"] {
    background: #050027;
}
        </style>
    """, unsafe_allow_html=True)
def user_profile_page():
    add_custom_css10()  
    
    st.markdown("# PERFIL DO USUÁRIO")
    
    if "cadastro" in st.session_state and st.session_state["cadastro"]["completed"]:
        st.write(f"**Nome da instituição**: {st.session_state['cadastro']['nome']}")
        st.write(f"**Rua**: {st.session_state['cadastro']['rua']}")
        st.write(f"**Bairro**: {st.session_state['cadastro']['bairro']}")
        st.write(f"**Número**: {st.session_state['cadastro']['numero']}")
        st.write(f"**CEP**: {st.session_state['cadastro']['cep']}")
        st.write(f"**Cidade**: {st.session_state['cadastro']['cidade']}")
        st.write(f"**Telefone**: {st.session_state['cadastro']['telefone']}")
    else:
        st.warning("Nenhum dado cadastrado encontrado. Por favor, faça o cadastro primeiro.")

    st.button("Voltar", on_click=navigate, args=("home",))

# Controle de navegação
if st.session_state["page"] == "welcome":
    welcome_page()
elif st.session_state["page"] == "register":
    register_page()
elif st.session_state["page"] == "login":
    login_page()
elif st.session_state["page"] == "home":
    home_page()
elif st.session_state["page"] == "upload_reference":
    upload_reference_page()
elif st.session_state["page"] == "upload_consent":
    upload_consent_page()
elif st.session_state["page"] == "upload_verification":
    upload_verification_page()
elif st.session_state["page"] == "registered_images_reference":
    registered_images_reference_page()
elif st.session_state["page"] == "registered_images_consent":
    registered_images_consent_page()
elif st.session_state["page"] == "user_profile":
    user_profile_page()