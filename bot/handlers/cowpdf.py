import os
from datetime import datetime
from aiogram import Router, F, types
from aiogram.types import FSInputFile
from weasyprint import HTML
from asgiref.sync import sync_to_async  # Django asinxron xatolikni oldini olish uchun

from app.models import CowBorn

# Router obyektini yaratish
dp = Router()

def generate_cow_pdf(cows_data) -> str:
    """Ma'lumotlarni chiroyli oq-ko'k PDF jadvalga aylantiruvchi funksiya"""
    pdf_path = f"cow_born_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Jadval qatorlarini generatsiya qilish
    table_rows = ""
    for index, cow in enumerate(cows_data, start=1):
        table_rows += f"""
        <tr>
            <td class="col-id">{index}</td>
            <td class="col-parent">{cow.parent}</td>
            <td class="col-date">{cow.date.strftime('%d.%m.%Y') if cow.date else '-'}</td>
        </tr>
        """

    # HTML va CSS dizayni (Oq va To'q Ko'k uslubida)
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
            .col-id {{ width: 10%; font-weight: bold; color: #1e3a8a; }}
            .col-parent {{ width: 60%; }}
            .col-date {{ width: 30%; color: #4a5568; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Yangi Tug'ilgan Buzoqlar Hisoboti</h1>
            <p>Yaratilgan vaqt: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>№</th>
                    <th>Chorva / ID (Parent)</th>
                    <th>Tug'ilgan Sana</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </body>
    </html>
    """

    # HTML faylni vaqtinchalik saqlash va PDF ga o'girish
    temp_html = f"temp_report_{datetime.now().timestamp()}.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    HTML(temp_html).write_pdf(pdf_path)
    os.remove(temp_html) # Vaqtinchalik faylni o'chiramiz
    
    return pdf_path

# Django ORM so'rovlarini asinxron muhitga moslashtirish funksiyasi
@sync_to_async
def get_cows_from_db():
    # evaluate (so'rovni bajarib ma'lumotni ro'yxat qilib olish)
    return list(CowBorn.objects.all())

@dp.callback_query(F.data == "cowpdf")
async def send_cow_report(callback: types.CallbackQuery):
    """Inline tugma bosilganda ishlovchi handler"""
    # Callback yuklanish aylanmasini to'xtatish (soat belgisini yo'qotadi)
    await callback.answer()
    
    # Kutish xabari
    waiting_msg = await callback.message.answer("🔄 Ma'lumotlar yig'ilmoqda va PDF tayyorlanmoqda, iltimos kuting...")
    
    try:
        # Bazadan ma'lumotlarni asinxron xavfsiz usulda olish
        cows_data = await get_cows_from_db()
        
        if not cows_data:
            await waiting_msg.edit_text("Bazada hech qanday ma'lumot topilmadi.")
            return

        # PDF generatsiya qilish
        pdf_file_path = generate_cow_pdf(cows_data)
        
        # Aiogram orqali PDF faylni yuborish
        document = FSInputFile(path=pdf_file_path, filename="Buzoqlar_Hisoboti.pdf")
        await callback.message.answer_document(
            document=document, 
            caption="📄 Sifati a'lo darajadagi PDF hisobot tayyor!"
        )
        
        # Kutish xabarini o'chirib tashlaymiz
        await waiting_msg.delete()
        
        # Yuborilgandan keyin serverdan o'chirib tashlash
        if os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)
            
    except Exception as e:
        await callback.message.answer(f"❌ Xatolik yuz berdi: {str(e)}")
        print(f"PDF Error: {e}")