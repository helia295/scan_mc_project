# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from turtle import update
from dash import Dash, html, dash_table, dcc
import pandas as pd
from dash.dependencies import Input, Output, State
import base64
import os
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory
import dash
import time
from dotenv import dotenv_values
import subprocess

__name__ = '__main__'
config = dotenv_values("./.env")


UPLOAD_DIRECTORY = config['UPLOAD_DIRECTORY']
SAMPLE_FILE = config['SAMPLE_FILE']
RELATED_URLS = config['RELATED_URLS']
RESULT_CSV = config['RESULT_CSV']
INTERVAL_MS = int(config['INTERVAL_MS'])
LOGO_PATH = "./assets/logo.png"

#to store current process
proc = None

encoded_image = base64.b64encode(open(LOGO_PATH, 'rb').read())

df = pd.read_csv(SAMPLE_FILE)

# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
external_scripts = [{'src':'./assets/custom_script.js'}]
server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_scripts = external_scripts)
app.title = 'CÔNG CỤ SCAN WEBSITE CỦA MERCHANT'


@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)

def server_layout():
    global proc
    if proc != None:
        proc.terminate()
    return html.Div([
        html.Div(children=[
            html.H1(
                children='CÔNG CỤ SCAN WEBSITE CỦA MERCHANT',
                style={
                    'fontFamily': "Times New Roman",
                    'fontSize': 28,
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
            'justifyContent': 'center',}
        ),
        
        html.H2("Bước 1: Chọn cách input website(s) cần scan.", 
            style = {
                'fontFamily': 'Times New Roman',
                'fontSize': 21,
                'fontWeight': 'bold',
                'marginLeft': '30px',}
        ),

        html.H4("Lựa chọn giữa upload toàn bộ danh sách merchants lên dưới dạng file csv HOẶC nhập thủ công từng link website để scan.",
                style = {
                    'fontFamily': 'Times New Roman',
                    'fontSize': 15,
                    'fontStyle': 'italic',
                    'textAlign': 'center',
                    'fontWeight': 'normal',}
        ),

        dcc.Dropdown(['Upload file CSV', 'Nhập url thủ công'], id='demo-dropdown',
                    style={
                            "width": "100%",
                            "height": "31px",
                            "lineHeight": "31px",
                            "textAlign": "center",
                            "marginLeft": "5px",
                            "fontFamily": "Times New Roman",
                            "color": "gray",
                            "fontSize": 15,
                            'marginBottom': '15px', 
                        },
        ),

        html.Div(id='dd-output-container',
                style = {
                    'fontFamily': 'Times New Roman',
                    'fontSize': 15,
                    'fontStyle': 'italic',
                    'textAlign': 'center',
                    'fontWeight': 'normal',
                    'color': 'blue',
                    'marginBottom': '20px',
                    'persistence': 'False'}
        ),

        html.Div([
            dcc.Input(
                    id="mc_input",
                    type="url",
                    placeholder="Nhập url vào đây. Ex: https://example.com/.",
                    debounce=True,
                    #required = "required",
                    )
            ], style= {}
        ),
        
        html.H2("Bước 2: Upload File(s).", 
            style = {
                'fontFamily': 'Times New Roman',
                'fontSize': 21,
                'fontWeight': 'bold',
                'marginLeft': '30px',}
        ),

        html.H4(id="upload-prompt", 
                style = {
                    'fontFamily': 'Times New Roman',
                    'fontSize': 15,
                    'fontStyle': 'italic',
                    'textAlign': 'center',
                    'fontWeight': 'normal',}
        ),

        dcc.Upload(
            id="upload-data",
            children=html.Div(
                ["Kéo thả hoặc Bấm vào đây để chọn file(s) cần upload."]
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
                "fontSize": 15,
            },
            multiple=True,
        ),
        
        html.H3("Danh sách File đã tải lên:",
                style = {
                    'fontFamily': 'Times New Roman',
                    'fontSize': 18,
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

        html.H2("Bước 3: Nhập số lượng link để scan cho mỗi Merchant.",
                style = {
                    'fontFamily': 'Times New Roman',
                    'fontSize': 21,
                    'fontWeight': 'bold',
                    'marginLeft': '30px',}
        ),

        html.H4("Giới hạn số lượng link phải scan cho mỗi Merchant sẽ giúp đẩy nhanh kết quả. Gợi ý: <=30 links/merchant.",
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

        html.H2("Bước 4: Bấm nút chạy lấy Kết quả.",
                style = {
                    'fontFamily': 'Times New Roman',
                    'fontSize': 21,
                    'fontWeight': 'bold',
                    'marginLeft': '30px',
                    'marginBottom': '10px',}
        ),
        
        html.Div([
        html.Button('Chạy chương trình', id='run', n_clicks=0,
        ),

        html.Button('Dừng chương trình', id='stop', n_clicks=0,
        ),
        ], style = {
                    'marginLeft': 'auto',
                    'marginRight': 'auto',
                    'marginBottom': '15px',
                    'verticalAlign': 'middle',
                    'display': 'flex',
                    'textAlign': 'center',
                    'alignItem': 'center',
                    'justifyContent': 'center',

        }),

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

        html.Div(id = "stop-validation", 
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

        html.Div([
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
                            columns=[
                                    {'name': 'Website', 'id': 'Website'},
                                    {'name': 'Keywords tìm thấy', 'id': 'Keywords tìm thấy'},
                                    {'name': 'Link liên kết ngoài', 'id': 'Link liên kết ngoài'},
                                    {'name': 'Người dùng đăng nhập', 'id': 'Người dùng đăng nhập'},
                                    {'name': 'Yêu cầu nạp tiền', 'id': 'Yêu cầu nạp tiền'}],
                            data=df.to_dict("records"),
                            page_size= 50,
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
                                } for d in ["Link liên kết ngoài", "Người dùng đăng nhập", "Yêu cầu nạp tiền"]
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
                                'fontSize': 15,
                                'fontFamily':'Times New Roman',
                                'textAlign': 'center',
                            }
                            )]
                    ),
                style = {
                    'position': 'absolute',
                    'marginTop': '30px',
                }
            ),
            dcc.Interval(
                id='interval-component',
                interval= INTERVAL_MS, # in milliseconds
                n_intervals=0,
            ),
        ]),
        
    ], style = {
        'marginRight': '40px',
        'marginLeft': '25px',
        'marginTop': '10px',
        'marginBottom': '30px',}
    )

app.layout = server_layout

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
    [Output('stop', 'style'), Output('stop', 'disabled'),
    Output('run', 'style'), Output('run', 'disabled')], 
    [Input('stop', 'n_clicks'), Input('run', 'n_clicks')])
def button_on_off(stop_clicks, n_clicks):
    run_button_on = {'backgroundColor': 'white',
                    'color': '#004d99',
                    'height': '30px',
                    'width': '200px',
                    'borderWidth': '1px',
                    'borderStyle': 'solid',
                    'borderColor': '#004d99',
                    'textAlign': 'center',
                    'fontFamily': 'Times New Roman',
                    'fontSize': 17,
                    'marginRight': 20,
                    'verticalAlign': 'middle',}
    run_button_off = {'backgroundColor': '#d3d3d3',
                    'color': '#616161',
                    'height': '30px',
                    'width': '200px',
                    'borderWidth': '1px',
                    'borderStyle': 'solid',
                    'borderColor': '#004d99',
                    'textAlign': 'center',
                    'fontFamily': 'Times New Roman',
                    'fontSize': 17,
                    'marginRight': 20,
                    'verticalAlign': 'middle',}
    stop_button_on = {'backgroundColor': 'white',
                    'color': 'red',
                    'height': '30px',
                    'width': '200px',
                    'borderWidth': '1px',
                    'borderStyle': 'solid',
                    'borderColor': 'red',
                    'textAlign': 'center',
                    'fontFamily': 'Times New Roman',
                    'fontSize': 17,
                    'verticalAlign': 'middle',}
    stop_button_off = {'backgroundColor': '#d3d3d3',
                    'color': '#616161',
                    'height': '30px',
                    'width': '200px',
                    'borderWidth': '1px',
                    'borderStyle': 'solid',
                    'borderColor': 'red',
                    'textAlign': 'center',
                    'fontFamily': 'Times New Roman',
                    'fontSize': 17,
                    'verticalAlign': 'middle',}
    if (n_clicks < 1) and (stop_clicks < 1):
        return [stop_button_off, True, run_button_on, False]
    elif (n_clicks >= 1) and (stop_clicks < 1):
        return [stop_button_on, False, run_button_off, True]
    elif (n_clicks < 1) and (stop_clicks >= 1):
        return [stop_button_off, True, run_button_on, False]
    elif (n_clicks >= 1) and (stop_clicks >= 1):
        return [stop_button_on, False, run_button_off, True]


@app.callback(
    [Output('dd-output-container', 'children'), Output('mc_input', 'style')],
    Input('demo-dropdown', 'value')
)
def update_output(value):
    if value == "Upload file CSV":
        return [f'Bạn đã chọn {value}. Xin mời thực hiện ở Bước 2!',
                {'display': 'none',}]
    elif value == "Nhập url thủ công":
        return [f'Bạn đã chọn {value}. Xin mời nhập link website của 1 Merchant cần scan ở ô dưới đây!', 
                {'display': 'inline',
                'textAlign': 'center',
                'fontSize': 15,
                'marginLeft':'10px',
                'height': '31px', 
                'width': '100%',
                'marginBottom': '5px', 
                'fontFamily': 'Times New Roman',
                'color': 'gray',
                }]
    else:
        return [None,{'display': 'none'}]


@app.callback(
    Output('upload-prompt', 'children'),
    Input('demo-dropdown', 'value')
)
def update_prompt(value):
    if value == "Nhập url thủ công":
        return "Hãy upload file danh sách Keywords (định dạng xls) ở đây!"
    else:
        return "Hãy upload file danh sách Keywords (định dạng xls) và file danh sách Merchants (định dạng csv) ở đây!"


@app.callback(
    Output("file-list", "children"),
    [Input("upload-data", "filename"), Input("upload-data", "contents"), Input("run", "n_clicks")],)
def update_file_list(uploaded_filenames, uploaded_file_contents, n_clicks):
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
    [Output('button-validation', 'children'), Output('run', 'n_clicks'),], 
    [Input('run', 'n_clicks'), Input('num_links', 'value'),
    Input('demo-dropdown', 'value'), Input('mc_input', 'value'),])
def button_validation(n_clicks, num_links, method, url):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if ("run" in changed_id):
        if n_clicks > 0:
            if os.path.isfile(RESULT_CSV):
                os.remove(RESULT_CSV)
            files = uploaded_files()
            if method == None:
                return ["Hãy chọn phương pháp upload danh sách MC ở Bước 1!", 0]
            if (method == "Nhập url thủ công") and ((url == None) or (url == "")):
                return ["Hãy nhập chính xác link website của Merchant cần scan ở Bước 1!", 0]
            if (method == "Nhập url thủ công") and ((len(files) < 1) or ("xls" not in files[0])):
                return ["Hãy upload file Keywords (định dạng xls) ở Bước 2!", 0]
            if (method == "Upload file CSV") and ((len(files) < 2) or (len(files) == 0)):
                return ["Hãy upload đủ 2 files Keywords và Merchants ở Bước 2!", 0]
            if (num_links == None) or (num_links < 1):
                return ["Hãy nhập số lớn hơn hoặc bằng 1 và không bao gồm các chữ cái ở Bước 3!", 0]
            if (num_links != None):
                return [None, 1]
        else:
            return [None, 0]
    else:
        return [None, 0]


@app.callback(
    [Output('stop-validation', 'children'), Output('stop', 'n_clicks')], 
    [Input('stop', 'n_clicks'), Input('run', 'n_clicks')])
def stop_validation(stop_clicks, n_clicks):
    global proc
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if ("stop" in changed_id):
        if stop_clicks > 0:
            if (proc != None) and (n_clicks >= 1):
                proc.terminate()
                return ["Chương trình đã dừng chạy! Để chạy lại từ đầu hãy xoá và thực hiện lại từ Bước 1.", 1]
            if (proc != None) and (n_clicks < 1):
                return ["Chương trình chưa bắt đầu chạy!", 0]
            if (proc == None) and (n_clicks < 1):
                return ["Chương trình chưa bắt đầu chạy!", 0]
            if (proc == None) and (n_clicks >= 1):
                return [None, 0]
        else:
            return [None, 0]
    else:
        return [None, 0]
        

@app.callback(
    [Output("upload-data", "filename"), Output("upload-data", "contents"),],
    [Input("upload-data", "filename"), Input("upload-data", "contents"), 
    Input("num_links", "value"), Input("run", "n_clicks"),
    Input('demo-dropdown', 'value'), Input('mc_input', 'value'),],
)
def run_code(uploaded_filenames, uploaded_file_contents, value, n_clicks, method, url):
    global proc
    if method == "Upload file CSV":
        if (n_clicks != None) and (n_clicks > 0):
            
            for filename in os.listdir(UPLOAD_DIRECTORY):
                path = os.path.join(UPLOAD_DIRECTORY, filename)
                if " " in filename:
                    filename = filename.replace(" ", "")
                    os.rename(path, os.path.join(UPLOAD_DIRECTORY, filename))
                    path = os.path.join(UPLOAD_DIRECTORY, filename)
                if os.path.isfile(path):
                    if "csv" in str(path):
                        mc_file = path
                    elif "xls" in str(path):
                        xlsfile = path
            
            #os.system('python3 run_scraper.py '+ mc_file + ' ' + xlsfile + ' ' + str(value) + ' ' + RELATED_URLS)
            
            proc = subprocess.Popen(['python3 run_scraper.py '+ mc_file + ' ' + xlsfile + ' ' + str(value) + ' ' + RELATED_URLS], shell=True)
            return [ None, None]

        else:
            return [uploaded_filenames, uploaded_file_contents]
    else:
        if (n_clicks != None) and (n_clicks > 0):
            
            for filename in os.listdir(UPLOAD_DIRECTORY):
                path = os.path.join(UPLOAD_DIRECTORY, filename)
                if " " in filename:
                    filename = filename.replace(" ", "")
                    os.rename(path, os.path.join(UPLOAD_DIRECTORY, filename))
                    path = os.path.join(UPLOAD_DIRECTORY, filename)
                if os.path.isfile(path):
                    if "xls" in str(path):
                        xlsfile = path

            #os.system('python3 run_scraper.py '+ url + ' ' + xlsfile + ' ' + str(value) + ' ' + RELATED_URLS)
            
            proc = subprocess.Popen(['python3 run_scraper.py '+ url + ' ' + xlsfile + ' ' + str(value) + ' ' + RELATED_URLS], shell=True)
            return [ None, None]

        else:
            return [ uploaded_filenames, uploaded_file_contents]


@app.callback(
    [Output("table-container", "data"), Output("button-running", "children")],
    [Input('interval-component', 'n_intervals'), Input("run", "n_clicks")]
)
def show_result(n_intervals, n_clicks):
    if n_intervals >= 0:
        if n_clicks > 0:
            try:
                res = pd.read_csv(RESULT_CSV, encoding="utf8")
            except:
                time.sleep(5)
                res = pd.read_csv(RESULT_CSV, encoding="utf8")

            count = len(res.to_dict("records"))
            if count > 0:
                return [res.to_dict("records"), "Đã scan xong "+str(count)+ " merchant(s)."]
            else:
                return [res.to_dict("records"), "Đang scan..."]
        else:
            a = pd.read_csv(SAMPLE_FILE, encoding="utf8")
            return [a.to_dict("records"), "Xin mời tham khảo sample!"]
    else:
        a = pd.read_csv(SAMPLE_FILE, encoding="utf8")
        return [a.to_dict("records"), "Xin mời tham khảo sample!"]

'''
if __name__ == '__main__':
    app.run_server(debug=True)
'''