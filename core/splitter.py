import os
import io
import msoffcrypto
import openpyxl
from datetime import datetime
from core.helpers import EXPORT_COLUMNS, col_letter_to_index, safe_str


def get_unique_dsc_company(ws) -> list:
    dsc_companies_set:set = set()
    dsc_companies:list = []
    last_row:int = ws.max_row
    for i in range(2, last_row+1):
        company = safe_str(ws.cell(row=i, column=1).value)
        if company not in dsc_companies_set:
            dsc_companies_set.add(company)
            dsc_companies.append(company)
    return dsc_companies


def build_export_workbook(source_ws, company_value:str)-> openpyxl.Workbook:
    new_wb = openpyxl.Workbook()
    new_ws = new_wb.active
    new_ws.title = "Data"

    new_index:list = [col_letter_to_index(col) for col in EXPORT_COLUMNS]

    for out_col, src_col_idx in enumerate(new_index, start=1):
        cell = new_ws.cell(row=1, column=out_col)
        cell.value =source_ws.cell(row=1, column=src_col_idx).value
        cell.font = openpyxl.styles.Font(bold=True)

    out_row = 2
    for src_row in range(2, source_ws.max_row + 1):
        row_company = safe_str(source_ws.cell(row=src_row, column=1).value)
        if row_company ==  company_value:
            for out_col, src_col_idx in enumerate(new_index, start=1):
                new_ws.cell(row=out_row, column=out_col).value = \
                    source_ws.cell(row=src_row, column=src_col_idx).value
            out_row += 1
    
    return new_wb


def protect_xlsx_with_password(wb, password:str):
    plain_buffer= io.BytesIO()
    wb.save(plain_buffer)
    plain_buffer.seek(0)
    encrypted_buffer = io.BytesIO()
    msoffcrypto.OfficeFile(plain_buffer).encrypt(password, encrypted_buffer)
    encrypted_buffer.seek(0)
    return encrypted_buffer.read()


def split_and_protect(processed_wb, output_folder, passwords:dict, progress_callback, status_callback):
    def update(pct: float, msg: str):
        if status_callback:
            status_callback(msg)
        if progress_callback:
            progress_callback(pct)

    ws = processed_wb.active
    timestamp:str = datetime.now().strftime("%Y_%m_%d_%H_%M")
    directory_path:str = f"{output_folder}/{timestamp}"
    os.makedirs(directory_path, exist_ok=True)
    created_files = []
    companies:list = get_unique_dsc_company(ws)
    if not companies:
        update(0.0, "Warning: Couldn't get companies.")
    num_companies:int = len(companies)
    
    progress:float = 0.88
    update(progress, f"{num_companies} found and ready to process.")
    for i, company in enumerate(companies):
        calc_i:float = (1.00-progress)/num_companies 
        company_wb = build_export_workbook(source_ws=ws, company_value=company)
        filename = f"{company}_NEW_GMC_{timestamp}.xlsx"
        filepath = os.path.join(directory_path, filename)
        company_pwd = passwords.get(company)
        if company_pwd and company_pwd.requires_password:
            protected_file = protect_xlsx_with_password(company_wb, company_pwd.password)
            with open(filepath, "wb") as f:
                f.write(protected_file)
            created_files.append(filepath)
        else:
            company_wb.save(filepath)
            created_files.append(filepath)
        progress+=calc_i
        update(progress, f"{company} complete")
    update(1.0, "Process complete...")
    return created_files
