import os
from datetime import datetime
from aiogram import Router, F, types
from aiogram.types import FSInputFile
from weasyprint import HTML
from asgiref.sync import sync_to_async

# O'zingizning ilovangiz nomidan Milk modelini chaqirasiz
from app.models import Milk

# Router obyektini yaratish
dp = Router()

def generate_milk_pdf(milk_data) -> str:
    """Ma'lumotlarni chiroyli oq-ko'k PDF jadvalga aylantiruvchi funksiya"""
    pdf_path = f"milk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Jadval qatorlarini generatsiya qilish
    table_rows = ""
    total_liters = 0  # Umumiy sut miqdorini hisoblash uchun
    
    for index, record in enumerate(milk_data, start=1):
        total_liters += record.litr
        table_rows += f"""
        <tr>
            <td class="col-id">{index}</td>
            <td class="col-litr">{record.litr} litr</td>
            <td class="col-date">{record.date.strftime('%d.%m.%Y') if record.date else '-'}</td>
        </tr>
        """

    # HTML va CSS dizayni
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 20mm 15mm;
                @bottom-right {{
                    content: "Sahifa " counter(page);
                    font-family: Arial, sans-serif;
                    font-size: 9pt;
                    color: #718096;
                }}
            }}
            body {{
                font-family: Arial, sans-serif;
                color: #2d3748;
                margin: 0;
                padding: 0;
            }}
            .header {{
                background-color: #0f4c81; /* To'q Ko'k */
                color: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 4px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 20pt;
            }}
            .header p {{
                margin: 5px 0 0 0;
                font-size: 10pt;
                color: #e2e8f0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            th {{
                background-color: #1e3a8a; /* Qirollik ko'k */
                color: white;
                padding: 12px;
                text-align: left;
                font-size: 11pt;
            }}
            td {{
                padding: 12px;
                border-bottom: 1px solid #e2e8f0;
                font-size: 10pt;
            }}
            tr:nth-child(even) td {{
                background-color: #f8fafc; /* Yengil och ko'k/kulrang fon */
            }}
            .total-row {{
                font-weight: bold;
                background-color: #e2e8f0 !important;
            }}
            .col-id {{ width: 15%; font-weight: bold; color: #1e3a8a; }}
            .col-litr {{ width: 45%; font-weight: bold; }}
            .col-date {{ width: 40%; color: #4a5568; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Sut Ishlab Chiqarish Hisoboti</h1>
            <p>Yaratilgan vaqt: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>№</th>
                    <th>Sut miqdori</th>
                    <th>Sana</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
                <tr class="total-row">
                    <td>Jami:</td>
                    <td>{total_liters} litr</td>
                    <td>-</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """

    # HTML faylni vaqtinchalik saqlash va PDF ga o'girish
    temp_html = f"temp_milk_report_{datetime.now().timestamp()}.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    HTML(temp_html).write_pdf(pdf_path)
    os.remove(temp_html) # Vaqtinchalik faylni o'chiramiz
    
    return pdf_path

# Django ORM so'rovini asinxron muhitga moslashtirish (Sanalari bo'yicha saralab olish qo'shildi)
@sync_to_async
def get_milk_data_from_db():
    return list(Milk.objects.all().order_by('-date'))

@dp.callback_query(F.data == "milkpdf")
async def send_milk_report(callback: types.CallbackQuery):
    """Inline tugma bosilganda ishlovchi handler"""
    await callback.answer()
    
    waiting_msg = await callback.message.answer("🔄 Sut hisoboti ma'lumotlari yig'ilmoqda va PDF tayyorlanmoqda...")
    
    try:
        # Bazadan ma'lumotlarni olish
        milk_data = await get_milk_data_from_db()
        
        if not milk_data:
            await waiting_msg.edit_text("Bazada sut miqdoriga oid hech qanday ma'lumot topilmadi.")
            return

        # PDF generatsiya qilish
        pdf_file_path = generate_milk_pdf(milk_data)
        
        # Aiogram orqali PDF faylni yuborish
        document = FSInputFile(path=pdf_file_path, filename="Sut_Hisoboti.pdf")
        await callback.message.answer_document(
            document=document, 
            caption="📄 Sut ishlab chiqarish bo'yicha PDF hisobot tayyor!"
        )
        
        await waiting_msg.delete()
        
        # Server xotirasini tozalamiz
        if os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)
            
    except Exception as e:
        await callback.message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
        print(f"Milk PDF Error: {e}")