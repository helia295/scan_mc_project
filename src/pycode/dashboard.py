# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from turtle import update
from dash import Dash, html, dash_table, dcc
import pandas as pd
from dash.dependencies import Input, Output
import base64
import os
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory
import dash
import time
from dotenv import dotenv_values

config = dotenv_values("./.env")


UPLOAD_DIRECTORY = config['UPLOAD_DIRECTORY']
SAMPLE_FILE = config['SAMPLE_FILE']
RELATED_URLS = config['RELATED_URLS']
LOGO_PATH = "./assets/logo.png"

encoded_image = base64.b64encode(open(LOGO_PATH, 'rb').read())

df = pd.read_csv(SAMPLE_FILE)


# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
server = Flask(__name__)
app = dash.Dash(server=server)
app.title = 'CÔNG CỤ SCAN WEBSITE CỦA MERCHANT'


@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


app.layout = html.Div([
    html.Div(children=[
        html.H1(
            children='CÔNG CỤ SCAN WEBSITE CỦA MERCHANT',
            style={
                'fontFamily': "Times New Roman",
                #'display':'inline-block',
                'fontSize': '28',
                'fontWeight': 'bold',
                #"color": "#0059b3",
                'display':'inline', 
                'paddingTop': '30px'}
        ),
        html.Img(src=("data:image/png;base64,{}").format(encoded_image.decode()),
                    style = {'display':'inline', 
                            'width': '95px', 
                            'height': '95px',
                            'padding': '15px'
                            })
    ], style={
        'display': 'flex',
        'textAlign': 'center',
        'alignItem': 'center',
        'justifyContent': 'center',
    }),
    
    html.H2("Bước 1: Upload 2 File Keywords (xls) & Merchants (csv)", 
        style = {
            'fontFamily': 'Times New Roman',
            'fontSize': '21',
            'fontWeight': 'bold',
            'marginLeft': '30px',}
    ),

    html.H4("Hãy upload file danh sách Keywords (định dạng xls) và file danh sách Merchants (định dạng csv)!",
            style = {
                'fontFamily': 'Times New Roman',
                'fontSize': '15',
                'fontStyle': 'italic',
                'textAlign': 'center',
                'fontWeight': 'normal',}
    ),

    dcc.Upload(
        id="upload-data",
        children=html.Div(
            ["Drag and drop or click to select a file to upload."]
        ),
        style={
            "width": "100%",
            "height": "31px",
            "lineHeight": "31px",
            "borderWidth": "1px",
            "borderStyle": "solid",
            "borderRadius": "2px",
            "textAlign": "center",
            "marginLeft": "10px",
            "fontFamily": "Times New Roman",
            "color": "gray",
            "fontSize": "15",
        },
        multiple=True,
    ),
    
    html.H3("Danh sách File đã tải lên:",
            style = {
                'fontFamily': 'Times New Roman',
                'fontSize': '18',
                'fontWeight': 'bold',
                'marginLeft': '30px',
                'marginTop': '20px',
                'color': '#004d99',}
    ),

    html.Ul(id="file-list", 
            style = {
                'fontFamily': 'Times New Roman',
                'marginLeft': '45px',}
    ),

    html.H2("Bước 2: Nhập số lượng link để scan cho mỗi Merchant",
            style = {
                'fontFamily': 'Times New Roman',
                'fontSize': 21,
                'fontWeight': 'bold',
                'marginLeft': '30px',}
    ),

    html.H4("Giới hạn số lượng link phải scan cho mỗi Merchant sẽ giúp đẩy nhanh kết quả. Gợi ý: <=50 links/merchant.",
            style = {
                'fontFamily': 'Times New Roman',
                'fontSize': 15,
                'fontStyle': 'italic',
                'textAlign': 'center',
                'fontWeight': 'normal',}
    ),

    dcc.Input(id="num_links", type="number", min=1,
            placeholder="Điền số links/merchant vào đây.", 
            style={'textAlign': 'center',
                    'fontSize': 15,
                    'marginLeft':'10px',
                    'height': '31px', 
                    'width': '100%',
                    'marginBottom': '5px', 
                    'fontFamily': 'Times New Roman',
                    'color': 'black'},
            debounce=True,
            #required = "required",
    ),

    html.H2("Bước 3: Bấm nút chạy lấy Kết quả",
            style = {
                'fontFamily': 'Times New Roman',
                'fontSize': 21,
                'fontWeight': 'bold',
                'marginLeft': '30px',
                'marginBottom': '10px',}
    ),

    
    html.Button('Chạy chương trình', id='run', n_clicks=0,
                style = {'backgroundColor': 'white',
                        'color': '#004d99',
                        'height': '30px',
                        'width': '200px',
                        'borderWidth': '1px',
                        'borderStyle': 'solid',
                        'borderColor': '#004d99',
                        'textAlign': 'center',
                        'fontFamily': 'Times New Roman',
                        'fontSize': 18,
                        'display': 'block',
                        'marginLeft': 'auto',
                        'marginRight': 'auto',
                        'marginBottom': '15px',
                        'verticalAlign': 'middle',}
    ),

    html.Div(id = "button-validation", 
            style = {
                'fontFamily': 'Times New Roman',
                'fontSize': 15,
                'fontStyle': 'italic',
                'textAlign': 'center',
                'fontWeight': 'normal',
                'color': 'red',
                'marginBottom': '20px',
                'persistence': 'False'}
    ),

    html.Div(id = "button-running", 
            style = {
                'fontFamily': 'Times New Roman',
                'fontSize': 15,
                'fontStyle': 'italic',
                'textAlign': 'center',
                'fontWeight': 'normal',
                'color': "blue",
                'marginBottom': '20px',
                'persistence': 'False'}
    ),
    dcc.Loading(
            id="loading-table",
            type="circle",
            children=html.Div(id='result-table', 
                    children=[dash_table.DataTable(
                    id="table-container",
                    columns=[{'name': 'STT', 'id': 'STT'},
                            {'name': 'Website', 'id': 'Website'},
                            {'name': 'Keywords tìm thấy', 'id': 'Keywords tìm thấy'},
                            {'name': 'Link liên kết ngoài', 'id': 'Link liên kết ngoài'},
                            {'name': 'Người dùng đăng nhập', 'id': 'Người dùng đăng nhập'},
                            {'name': 'Yêu cầu nạp tiền', 'id': 'Yêu cầu nạp tiền'}],
                    data=df.to_dict("records"),
                    style_table = {"marginLeft": "10px","marginRight": "50px",},
                    style_cell_conditional=[
                        {
                            'if': {'column_id': c},
                            'textAlign': 'left',
                        } for c in ["Website", "Keywords tìm thấy"]
                    ] + [
                        {
                            'if': {'column_id': d},
                            'textAlign': 'center',
                        } for d in ["STT", "Link liên kết ngoài", "Người dùng đăng nhập", "Yêu cầu nạp tiền"]
                    ],
                    style_cell={
                        'height': 'auto',
                        'width': 'auto',
                        'whiteSpace': 'normal',
                    },
                    style_data={
                        'color': 'black',
                        'backgroundColor': 'white',
                        'fontFamily':'Times New Roman',
                        'overflowX': 'auto'
                    },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': '#cce7ff',
                        }
                    ],
                    style_header={
                        'backgroundColor': '#66b3ff',
                        'color': 'black',
                        'fontWeight': 'bold',
                        'fontSize': 16,
                        'fontFamily':'Times New Roman',
                        'textAlign': 'center',
                    }
                    )]
            ),
        style = {
            'position': 'absolute',
            'marginBottom': '700px',
        }
    ),
], style = {
    'marginRight': '40px',
    'marginLeft': '25px',
    'marginTop': '10px',
    'marginBottom': '30px',}
)


def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


@app.callback(
    Output("file-list", "children"),
    [Input("upload-data", "filename"), Input("upload-data", "contents")],)
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""
    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)

    files = uploaded_files()
    if len(files) == 0:
        return [html.Li("Chưa có file nào!", style = {"color": "#004d99","marginBottom": "10px","fontFamily":"Times New Roman",})]
    else:
        return [html.Li(file_download_link(filename), style = {"color": "#004d99","marginBottom": "10px","fontFamily":"Times New Roman",}) for filename in files]


@app.callback(
    [Output('button-validation', 'children'), Output('run', 'n_clicks')], 
    [Input('run', 'n_clicks'),Input('num_links', 'value') ])
def button_validation(n_clicks, num_links):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if ("run" in changed_id):
        if n_clicks > 0:
            files = uploaded_files()
            if len(files) < 2:
                return ["Hãy upload đủ 2 files Keywords và Merchants ở Bước 1!", 0]
            if (num_links == None) or (num_links < 1):
                return ["Hãy nhập số lớn hơn hoặc bằng 1 và không bao gồm các chữ cái ở Bước 2!", 0]
            if num_links != None:
                return [None, 1]
        else:
            return [None, 0]
    else:
        return [None, 0]
        

@app.callback(
    [Output("table-container", "data"), Output("button-running", "children")],
    [Input("upload-data", "filename"), Input("upload-data", "contents"), Input("num_links", "value"), Input("run", "n_clicks")],)
def generate_table(uploaded_filenames, uploaded_file_contents, value, n_clicks):
        dict_list = []
        print(n_clicks)
    #changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    #if ("run" in changed_id):
        if (n_clicks != None) and (n_clicks > 0):
            from src.pycode.scraper.scraper import get_URLs_to_list, getKeywordstoList, configure_chrome_driver, findKeyword
            
            for filename in os.listdir(UPLOAD_DIRECTORY):
                path = os.path.join(UPLOAD_DIRECTORY, filename)
                if os.path.isfile(path):
                    if "csv" in str(path):
                        mc_file = path
                    elif "xls" in str(path):
                        xlsfile = path
            
            # Get a list of start URLs to scan
            start_URLs = get_URLs_to_list(mc_file)

            # Get a list of keywords to scan
            wordlist = getKeywordstoList(xlsfile)

            driver = configure_chrome_driver()
            
            stt = 0
            for web in start_URLs[0:5]:
                web_dict = findKeyword(driver, web, wordlist, stt, value, RELATED_URLS)
                if web_dict != {}:
                    #print(web_dict)
                    dict_list.append(web_dict)
                    stt+=1
            
            return [dict_list, "Đã scan xong!"]

        else:
            a = pd.read_csv(SAMPLE_FILE)
            return [a.to_dict("records"), None]

'''
if __name__ == '__main__':
    app.run_server(debug=True)
'''