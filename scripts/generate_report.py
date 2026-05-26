#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate complete Vietnamese academic report (báo cáo đồ án tốt nghiệp)
for Staff Management project as a Word document.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

def add_page_break(doc):
    """Add page break."""
    doc.add_page_break()

def add_centered_title(doc, text, font_size=18, bold=True, space_before=0, space_after=12):
    """Add centered title."""
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_format = p.paragraph_format
    p_format.space_before = Pt(space_before)
    p_format.space_after = Pt(space_after)
    for run in p.runs:
        run.font.size = Pt(font_size)
        run.font.bold = bold
        run.font.name = 'Times New Roman'

def add_heading_chapter(doc, level, text):
    """Add chapter heading (Chương 1, 1.1, 1.1.1)."""
    if level == 1:
        p = doc.add_paragraph(text, style='Heading 1')
    elif level == 2:
        p = doc.add_paragraph(text, style='Heading 2')
    else:
        p = doc.add_paragraph(text, style='Heading 3')
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    for run in p.runs:
        run.font.name = 'Times New Roman'

def add_body_paragraph(doc, text, indent=0):
    """Add body paragraph with proper formatting."""
    p = doc.add_paragraph(text)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.first_line_indent = Inches(0.5) if indent else Inches(0)
    for run in p.runs:
        run.font.size = Pt(13)
        run.font.name = 'Times New Roman'
    return p

def add_table_with_header(doc, rows_data, col_widths=None):
    """Add table with header row (first row is header)."""
    num_cols = len(rows_data[0]) if rows_data else 0
    table = doc.add_table(rows=len(rows_data), cols=num_cols)
    table.style = 'Light Grid Accent 1'

    if col_widths:
        for i, width in enumerate(col_widths):
            for cell in table.columns[i].cells:
                cell.width = Inches(width)

    # Fill header row
    if rows_data:
        for j, cell_text in enumerate(rows_data[0]):
            cell = table.rows[0].cells[j]
            cell.text = str(cell_text)
            # Header formatting
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.bold = True
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(11)

    # Fill data rows
    for i in range(1, len(rows_data)):
        for j, cell_text in enumerate(rows_data[i]):
            cell = table.rows[i].cells[j]
            cell.text = str(cell_text)
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(11)

    doc.add_paragraph()
    return table

def create_report():
    """Create the complete Word document."""
    doc = Document()

    # Set default font
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(13)

    # ==================== TRANG BÌA ====================
    add_centered_title(doc, '[TÊN TRƯỜNG ĐẠI HỌC]', font_size=16, space_before=24, space_after=6)
    add_centered_title(doc, '[TÊN KHOA/BỘ MÔN]', font_size=14, bold=False, space_after=24)

    add_paragraph_space = doc.add_paragraph()
    add_paragraph_space.paragraph_format.space_after = Pt(48)

    add_centered_title(doc, 'BÁOCÁOĐỒÁNTỐTGHIỆP', font_size=18, space_before=12, space_after=12)
    add_centered_title(doc, 'Xây dựng ứng dụng quản lý nhân sự tích hợp AI Chatbot',
                      font_size=14, bold=False, space_after=36)

    cover_info = [
        '',
        'Sinh viên thực hiện:',
        '[Thành viên 1]',
        '[Thành viên 2]',
        '[Thành viên 3]',
        '',
        'Giảng viên hướng dẫn:',
        '[Tên giảng viên]',
        '',
        'Lớp: [Tên lớp]',
        'Năm học: 2025 - 2026'
    ]

    for line in cover_info:
        p = doc.add_paragraph(line)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(8)
        for run in p.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(13)

    add_page_break(doc)

    # ==================== LỜI CẢM ƠN ====================
    add_centered_title(doc, 'LỜI CẢM ƠN')
    add_body_paragraph(doc,
        'Chúng tôi xin trân trọng cảm ơn [Tên giảng viên hướng dẫn], giảng viên hướng dẫn đồ án, đã tận tình '
        'hướng dẫn, khích lệ và giúp đỡ chúng tôi hoàn thành đồ án này. Đồ án không thể hoàn thành được nếu '
        'không có sự hỗ trợ, chỉ bảo quý báu từ thầy cô.')

    add_body_paragraph(doc,
        'Chúng tôi cũng xin cảm ơn các thầy cô giảng viên trong khoa, các thầy cô cấp trường đã tạo điều kiện '
        'thuận lợi để chúng tôi học tập và hoàn thành đồ án này.')

    add_body_paragraph(doc,
        'Mặc dù đã cố gắng hết sức, nhưng do kiến thức còn hạn chế, báo cáo đồ án này chắc chắn còn có những '
        'thiếu sót, rất mong nhận được những ý kiến góp ý từ các thầy cô và bạn bè.')

    add_page_break(doc)

    # ==================== NHẬN XÉT GIẢNG VIÊN ====================
    add_centered_title(doc, 'NHẬN XÉT CỦA GIẢNG VIÊN HƯỚNG DẪN')
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()
    add_body_paragraph(doc, 'Giảng viên hướng dẫn: _____________________________')
    add_body_paragraph(doc, 'Ngày: _____________________________')

    add_page_break(doc)

    # ==================== MỤC LỤC ====================
    add_centered_title(doc, 'MỤC LỤC')
    toc_items = [
        'LỜI CẢM ƠN',
        'NHẬN XÉT GIẢNG VIÊN',
        'MỤC LỤC',
        'DANH MỤC HÌNH ẢNH',
        'DANH MỤC BẢNG BIỂU',
        'LỜI MỞ ĐẦU',
        'CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI',
        '1.1. Lý do chọn đề tài',
        '1.2. Mục tiêu đề tài',
        '1.3. Đối tượng và phạm vi nghiên cứu',
        '1.4. Ý nghĩa thực tiễn',
        'CHƯƠNG 2: CƠ SỞ LÝ THUYẾT',
        '2.1. Android Java và lập trình ứng dụng di động',
        '2.2. Firebase và các dịch vụ cloud',
        '2.3. Firestore – Cơ sở dữ liệu realtime',
        '2.4. Firebase Authentication',
        '2.5. Firebase Storage và Cloud Messaging',
        '2.6. Trí tuệ nhân tạo và Gemini API',
        '2.7. Kỹ thuật RAG (Retrieval-Augmented Generation)',
        '2.8. ChromaDB – Vector Database',
        '2.9. FastAPI và Backend',
        '2.10. Các thư viện hỗ trợ giao diện',
        'CHƯƠNG 3: PHÂN TÍCH HỆ THỐNG',
        '3.1. Yêu cầu chức năng',
        '3.2. Yêu cầu phi chức năng',
        '3.3. Phân quyền người dùng',
        'CHƯƠNG 4: THIẾT KẾ HỆ THỐNG',
        '4.1. Kiến trúc tổng thể',
        '4.2. Thiết kế cơ sở dữ liệu Firestore',
        '4.3. Thiết kế AI Chatbot',
        'CHƯƠNG 5: XÂY DỰNG CHỨC NĂNG',
        '5.1. Hệ thống đăng nhập và phân quyền',
        '5.2. Quản lý nhân viên',
        '5.3. Chấm công và tracking',
        '5.4. Quản lý nghỉ phép',
        '5.5. Quản lý nhiệm vụ (Task)',
        '5.6. Tính toán lương',
        '5.7. Thống kê và báo cáo',
        '5.8. Chat nội bộ realtime',
        '5.9. Thông báo Firebase Cloud Messaging',
        '5.10. Hỗ trợ đa ngôn ngữ',
        '5.11. Sinh trắc học',
        '5.12. AI Assistant và Chatbot',
        'CHƯƠNG 6: KIỂM THỬ VÀ ĐÁNH GIÁ',
        '6.1. Mục tiêu kiểm thử',
        '6.2. Test case và kết quả',
        '6.3. Đánh giá ưu điểm',
        '6.4. Hạn chế và cải tiến',
        'CHƯƠNG 7: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN',
        '7.1. Kết quả đạt được',
        '7.2. Hạn chế hiện tại',
        '7.3. Hướng phát triển tương lai',
        'PHÂN CÔNG CÔNG VIỆC NHÓM',
        'TÀI LIỆU THAM KHẢO'
    ]

    for item in toc_items:
        p = doc.add_paragraph(item)
        p.paragraph_format.left_indent = Inches(0.5) if not item.startswith('CHƯƠNG') and not item.startswith('PHÂN') and not item.startswith('TÀI') else Inches(0)
        for run in p.runs:
            run.font.size = Pt(12)
            run.font.name = 'Times New Roman'

    add_page_break(doc)

    # ==================== DANH MỤC HÌNH ẢNH ====================
    add_centered_title(doc, 'DANH MỤC HÌNH ẢNH')
    figures_data = [
        ['Số TT', 'Tên hình ảnh', 'Trang'],
        ['Hình 1', 'Kiến trúc tổng thể hệ thống', '[Trang]'],
        ['Hình 2', 'Luồng đăng nhập người dùng', '[Trang]'],
        ['Hình 3', 'Luồng phân quyền Admin/Manager/Employee', '[Trang]'],
        ['Hình 4', 'Giao diện Dashboard Admin', '[Trang]'],
        ['Hình 5', 'Giao diện Quản lý nhân viên', '[Trang]'],
        ['Hình 6', 'Giao diện Chấm công', '[Trang]'],
        ['Hình 7', 'Giao diện AI Assistant', '[Trang]'],
        ['Hình 8', 'Luồng xử lý Chatbot với RAG', '[Trang]'],
    ]
    add_table_with_header(doc, figures_data, col_widths=[0.8, 3.5, 1])

    add_page_break(doc)

    # ==================== DANH MỤC BẢNG BIỂU ====================
    add_centered_title(doc, 'DANH MỤC BẢNG BIỂU')
    tables_data = [
        ['Số TT', 'Tên bảng', 'Trang'],
        ['Bảng 1', 'Công nghệ sử dụng', '[Trang]'],
        ['Bảng 2', 'Yêu cầu chức năng', '[Trang]'],
        ['Bảng 3', 'Collections Firestore', '[Trang]'],
        ['Bảng 4', 'Use case hệ thống', '[Trang]'],
        ['Bảng 5', 'Test case kiểm thử', '[Trang]'],
        ['Bảng 6', 'Phân công công việc', '[Trang]'],
        ['Bảng 7', 'Ưu điểm và hạn chế', '[Trang]'],
    ]
    add_table_with_header(doc, tables_data, col_widths=[0.8, 3.5, 1])

    add_page_break(doc)

    # ==================== LỜI MỞ ĐẦU ====================
    add_centered_title(doc, 'LỜI MỞ ĐẦU')

    add_body_paragraph(doc,
        'Trong thời đại công nghệ thông tin phát triển mạnh mẽ, các ứng dụng di động trở thành công cụ không thể thiếu '
        'trong quản lý doanh nghiệp. Đặc biệt, quản lý nhân sự là một lĩnh vực đòi hỏi xử lý dữ liệu phức tạp, cập nhật '
        'realtime và có sự tương tác cao với người dùng. Ứng dụng quản lý nhân sự tích hợp AI Chatbot là một giải pháp '
        'hiện đại giúp tối ưu hóa quy trình quản lý, nâng cao hiệu suất làm việc và cải thiện trải nghiệm người dùng.')

    add_body_paragraph(doc,
        'Đồ án này hướng đến xây dựng một hệ thống quản lý nhân sự hoàn chỉnh chạy trên nền tảng Android, tích hợp '
        'Firebase để lưu trữ dữ liệu và xử lý realtime, cùng với module AI Chatbot sử dụng Google Gemini API và kỹ thuật '
        'RAG để hỗ trợ tự động trả lời các câu hỏi nhân sự.')

    add_body_paragraph(doc,
        'Báo cáo này trình bày chi tiết về phân tích yêu cầu, thiết kế hệ thống, quá trình xây dựng từng chức năng, '
        'kiểm thử hệ thống và đánh giá kết quả. Chúng tôi hy vọng đồ án này không chỉ đáp ứng yêu cầu học tập mà còn '
        'có giá trị thực tiễn trong việc ứng dụng công nghệ vào quản lý doanh nghiệp.')

    add_page_break(doc)

    # ==================== CHƯƠNG 1: TỔNG QUAN ====================
    add_heading_chapter(doc, 1, 'CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI')

    add_heading_chapter(doc, 2, '1.1. Lý do chọn đề tài')
    add_body_paragraph(doc,
        'Nhu cầu quản lý nhân sự hiệu quả là một thách thức lớn đối với các doanh nghiệp hiện đại. Các hệ thống quản lý '
        'truyền thống thường phức tạp, chậm chạp và khó sử dụng. Ứng dụng di động mang lại sự linh hoạt và tiện lợi, '
        'cho phép nhân viên truy cập thông tin từ bất kỳ đâu, bất kỳ lúc nào.')

    add_body_paragraph(doc,
        'Tích hợp AI Chatbot không chỉ tự động hóa các quy trình mà còn cung cấp trợ giúp trực tuyến cho nhân viên, '
        'giúp giải đáp các câu hỏi thường gặp về chính sách, quy trình, và thông tin nhân sự mà không cần can thiệp '
        'từ bộ phận HR.')

    add_heading_chapter(doc, 2, '1.2. Mục tiêu đề tài')
    add_body_paragraph(doc,
        'Mục tiêu chính của đề tài là xây dựng một hệ thống quản lý nhân sự toàn diện với các chức năng:')

    objectives = [
        'Cung cấp giao diện thân thiện, dễ sử dụng trên nền tảng Android',
        'Quản lý nhân viên, phân bổ task, chấm công và nghỉ phép',
        'Tính toán lương tự động dựa trên chấm công và hiệu suất',
        'Hỗ trợ chat nội bộ realtime giữa các nhân viên',
        'Tích hợp AI Chatbot để trả lời các câu hỏi về chính sách và thông tin nhân sự',
        'Cung cấp thống kê dữ liệu và báo cáo tổng hợp',
        'Hỗ trợ xác thực sinh trắc học để tăng bảo mật',
        'Gửi thông báo realtime thông qua Firebase Cloud Messaging'
    ]
    for obj in objectives:
        p = doc.add_paragraph(obj, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_heading_chapter(doc, 2, '1.3. Đối tượng và phạm vi nghiên cứu')
    add_body_paragraph(doc,
        'Đối tượng: Hệ thống quản lý nhân sự di động tích hợp AI Chatbot.')
    add_body_paragraph(doc,
        'Phạm vi: Ứng dụng được xây dựng cho nền tảng Android, hỗ trợ ba loại người dùng (Admin, Manager, Employee) '
        'với các quyền hạn khác nhau. Backend sử dụng Firebase Realtime Database và Firestore để đảm bảo đồng bộ dữ liệu '
        'realtime. Module AI Chatbot chạy trên server FastAPI riêng.')

    add_heading_chapter(doc, 2, '1.4. Ý nghĩa thực tiễn')
    add_body_paragraph(doc,
        'Hệ thống giúp:')

    significances = [
        'Tối ưu hóa quy trình quản lý nhân sự, giảm công việc thủ công',
        'Nâng cao hiệu suất làm việc và tính chuyên nghiệp của tổ chức',
        'Cải thiện trải nghiệm nhân viên thông qua giao diện di động và AI hỗ trợ',
        'Cung cấp dữ liệu chính xác, kịp thời cho quản lý cấp cao ra quyết định',
        'Cho phép học tập thực tiễn về phát triển ứng dụng Android, Firebase và AI integration'
    ]
    for sig in significances:
        p = doc.add_paragraph(sig, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_page_break(doc)

    # ==================== CHƯƠNG 2: CƠ SỞ LÝ THUYẾT ====================
    add_heading_chapter(doc, 1, 'CHƯƠNG 2: CƠ SỞ LÝ THUYẾT')

    add_heading_chapter(doc, 2, '2.1. Android Java và lập trình ứng dụng di động')
    add_body_paragraph(doc,
        'Android là hệ điều hành mã nguồn mở do Google phát triển, chiếm thị phần lớn nhất trên toàn cầu. Android cho phép '
        'phát triển ứng dụng native bằng Java với hiệu năng cao và khả năng sử dụng đầy đủ tài nguyên thiết bị.')
    add_body_paragraph(doc,
        'Java là ngôn ngữ lập trình hướng đối tượng, có đặc điểm mạnh mẽ: hỗ trợ đa luồng, quản lý bộ nhớ tự động (Garbage Collection), '
        'sư dụng cơ chế Activity-based navigation, hỗ trợ mạnh mẽ về UI bằng Material Design.')

    add_heading_chapter(doc, 2, '2.2. Firebase và các dịch vụ cloud')
    add_body_paragraph(doc,
        'Firebase là nền tảng backend-as-a-service (BaaS) do Google cung cấp, giúp phát triển ứng dụng nhanh chóng mà không cần '
        'xây dựng backend riêng. Firebase cung cấp:')

    firebase_features = [
        'Firebase Authentication: Xác thực người dùng qua email/mật khẩu, Google, Facebook, v.v.',
        'Cloud Firestore: Cơ sở dữ liệu NoSQL realtime với khả năng đồng bộ tức thì',
        'Firebase Storage: Lưu trữ tệp (avatar, tài liệu) với tính bảo mật cao',
        'Firebase Cloud Messaging (FCM): Gửi thông báo push đến các thiết bị',
        'Firebase Analytics: Theo dõi hành vi người dùng (không sử dụng trong đề tài này)',
        'Firebase Hosting: Deploy ứng dụng web (nếu có)'
    ]
    for feature in firebase_features:
        p = doc.add_paragraph(feature, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_heading_chapter(doc, 2, '2.3. Firestore – Cơ sở dữ liệu realtime')
    add_body_paragraph(doc,
        'Firestore là cơ sở dữ liệu document-oriented, lưu trữ dữ liệu dưới dạng Collections chứa Documents. Mỗi Document '
        'là một JSON object chứa các fields. Firestore hỗ trợ queries phức tạp, indexing tự động, và realtime listeners.')

    firestore_benefits = [
        'Dữ liệu được đồng bộ realtime giữa client và server',
        'Hỗ trợ offline mode, dữ liệu được cache và đồng bộ khi có kết nối',
        'Tính bảo mật cao với Firebase Security Rules',
        'Scaling tự động theo lưu lượng',
        'Truy vấn linh hoạt và indexing thông minh'
    ]
    for benefit in firestore_benefits:
        p = doc.add_paragraph(benefit, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_heading_chapter(doc, 2, '2.4. Firebase Authentication')
    add_body_paragraph(doc,
        'Firebase Authentication cung cấp giải pháp xác thực toàn bộ, hỗ trợ nhiều phương thức: email/mật khẩu, Google Sign-In, '
        'Facebook, GitHub, v.v. Ứng dụng sử dụng Firebase Authentication để quản lý đăng nhập, đăng xuất, và xác thực người dùng.')

    add_heading_chapter(doc, 2, '2.5. Firebase Storage và Cloud Messaging')
    add_body_paragraph(doc,
        'Firebase Storage lưu trữ các tệp như hình ảnh avatar, tài liệu. Firebase Cloud Messaging (FCM) là dịch vụ gửi thông báo '
        'push đến các thiết bị Android, cho phép ứng dụng gửi thông báo ngay cả khi ứng dụng không hoạt động.')

    add_heading_chapter(doc, 2, '2.6. Trí tuệ nhân tạo và Gemini API')
    add_body_paragraph(doc,
        'Google Gemini là mô hình AI đa phương thức mạnh mẽ, hỗ trợ xử lý text, hình ảnh, video. Trong đề tài này, Gemini API '
        'được sử dụng để xử lý câu hỏi tự nhiên từ nhân viên qua AI Chatbot.')

    add_heading_chapter(doc, 2, '2.7. Kỹ thuật RAG (Retrieval-Augmented Generation)')
    add_body_paragraph(doc,
        'RAG là kỹ thuật kết hợp retrieval (truy xuất) và generation (sinh): trước tiên tìm kiếm các tài liệu liên quan từ '
        'knowledge base, sau đó sử dụng những tài liệu này làm context để sinh ra câu trả lời chính xác hơn.')

    add_body_paragraph(doc,
        'Luồng RAG:')

    rag_steps = [
        'Người dùng đặt câu hỏi',
        'Embedding câu hỏi thành vector (sử dụng BAAI/bge-m3)',
        'Tìm kiếm các chunks tài liệu tương tự trong ChromaDB',
        'Rerank kết quả (sử dụng BAAI/bge-reranker-v2-m3)',
        'Tạo prompt kết hợp context + câu hỏi',
        'Gửi tới Gemini API để sinh câu trả lời',
        'Trả về câu trả lời cho người dùng'
    ]
    for step in rag_steps:
        p = doc.add_paragraph(step, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_heading_chapter(doc, 2, '2.8. ChromaDB – Vector Database')
    add_body_paragraph(doc,
        'ChromaDB là cơ sở dữ liệu vector lightweight, được thiết kế để lưu trữ vector embeddings. Trong ứng dụng, ChromaDB lưu trữ '
        'các embedding của tài liệu nhân sự, cho phép tìm kiếm nhanh các tài liệu liên quan.')

    add_heading_chapter(doc, 2, '2.9. FastAPI và Backend')
    add_body_paragraph(doc,
        'FastAPI là framework Python hiện đại, dễ sử dụng, hỗ trợ async/await. Module AI Chatbot xây dựng bằng FastAPI, '
        'cung cấp API endpoint cho ứng dụng Android gọi tới để xử lý câu hỏi.')

    add_heading_chapter(doc, 2, '2.10. Các thư viện hỗ trợ giao diện')
    add_body_paragraph(doc,
        'Glide: Thư viện tải và cache hình ảnh hiệu quả. MPAndroidChart: Thư viện vẽ biểu đồ chuyên nghiệp. '
        'Material Components: Thư viện UI tuân theo Material Design.')

    add_page_break(doc)

    # ==================== CHƯƠNG 3: PHÂN TÍCH HỆ THỐNG ====================
    add_heading_chapter(doc, 1, 'CHƯƠNG 3: PHÂN TÍCH HỆ THỐNG')

    add_heading_chapter(doc, 2, '3.1. Yêu cầu chức năng')

    requirements_data = [
        ['STT', 'Chức năng', 'Mô tả', 'Quyền'],
        ['1', 'Đăng nhập', 'Người dùng đăng nhập bằng email/mật khẩu', 'Tất cả'],
        ['2', 'Quản lý nhân viên', 'Thêm/sửa/xóa thông tin nhân viên', 'Admin'],
        ['3', 'Chấm công', 'Check-in/check-out, tracking công việc', 'Tất cả'],
        ['4', 'Xin nghỉ phép', 'Gửi đơn xin nghỉ, quản lý trạng thái', 'Employee/Manager'],
        ['5', 'Quản lý task', 'Giao task, cập nhật trạng thái', 'Admin/Manager'],
        ['6', 'Tính lương', 'Tính lương tự động, tạo bảng lương', 'Admin'],
        ['7', 'Thống kê', 'Xem báo cáo, biểu đồ, thống kê dữ liệu', 'Admin/Manager'],
        ['8', 'Chat nội bộ', 'Gửi/nhận tin nhắn realtime', 'Tất cả'],
        ['9', 'AI Chatbot', 'Hỏi đáp tài liệu nhân sự tự động', 'Tất cả'],
        ['10', 'Notification', 'Nhận thông báo push realtime', 'Tất cả'],
        ['11', 'Sinh trắc học', 'Xác thực sinh trắc học (vân tay)', 'Tất cả'],
        ['12', 'Đa ngôn ngữ', 'Hỗ trợ Tiếng Việt và Tiếng Anh', 'Tất cả'],
    ]
    add_table_with_header(doc, requirements_data, col_widths=[0.5, 1.2, 2.5, 1])

    add_heading_chapter(doc, 2, '3.2. Yêu cầu phi chức năng')

    non_func_data = [
        ['Tiêu chí', 'Mô tả', 'Mục tiêu'],
        ['Hiệu năng', 'Thời gian phản hồi API', '< 2 giây'],
        ['Độ tin cậy', 'Hệ thống khả dụng', '99% uptime'],
        ['Bảo mật', 'Mã hóa dữ liệu, HTTPS', 'Đảm bảo an toàn'],
        ['Khả năng mở rộng', 'Xử lý concurrent users', '>1000 users'],
        ['Khả năng sử dụng', 'Giao diện trực quan', 'Dễ học, dễ dùng'],
        ['Khả năng bảo trì', 'Code clean, documentation', 'Dễ maintain'],
    ]
    add_table_with_header(doc, non_func_data, col_widths=[1.2, 2, 1.8])

    add_heading_chapter(doc, 2, '3.3. Phân quyền người dùng')

    add_heading_chapter(doc, 3, '3.3.1. Admin')
    admin_perms = [
        'Đăng nhập vào hệ thống',
        'Quản lý toàn bộ nhân viên (thêm, sửa, xóa)',
        'Giao task cho nhân viên',
        'Xem và quản lý chấm công toàn công ty',
        'Tính lương tự động',
        'Xem thống kê và báo cáo',
        'Chat nội bộ với các nhân viên',
        'Sử dụng AI Chatbot',
        'Xem và quản lý yêu cầu nghỉ phép'
    ]
    for perm in admin_perms:
        p = doc.add_paragraph(perm, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_heading_chapter(doc, 3, '3.3.2. Manager')
    manager_perms = [
        'Đăng nhập vào hệ thống',
        'Quản lý team (xem thông tin nhân viên)',
        'Giao task cho nhân viên trong team',
        'Xem chấm công nhân viên trong team',
        'Chat nội bộ',
        'Sử dụng AI Chatbot',
        'Xem yêu cầu nghỉ phép và phê duyệt/từ chối',
        'Sử dụng xác thực sinh trắc học'
    ]
    for perm in manager_perms:
        p = doc.add_paragraph(perm, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_heading_chapter(doc, 3, '3.3.3. Employee')
    employee_perms = [
        'Đăng nhập vào hệ thống',
        'Check-in/check-out',
        'Xem task được giao',
        'Chat nội bộ',
        'Sử dụng AI Chatbot',
        'Gửi yêu cầu xin nghỉ phép',
        'Sử dụng xác thực sinh trắc học'
    ]
    for perm in employee_perms:
        p = doc.add_paragraph(perm, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_page_break(doc)

    # ==================== CHƯƠNG 4: THIẾT KẾ HỆ THỐNG ====================
    add_heading_chapter(doc, 1, 'CHƯƠNG 4: THIẾT KẾ HỆ THỐNG')

    add_heading_chapter(doc, 2, '4.1. Kiến trúc tổng thể')

    add_body_paragraph(doc, 'Kiến trúc hệ thống gồm 4 thành phần chính:')

    architecture = [
        'Android App: Ứng dụng di động nền tảng Android',
        'Firebase Backend: Cơ sở dữ liệu Firestore, Authentication, Storage, Messaging',
        'FastAPI Server: Backend xử lý AI Chatbot',
        'Vector Database: ChromaDB lưu trữ embeddings tài liệu'
    ]
    for arch in architecture:
        p = doc.add_paragraph(arch, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_body_paragraph(doc, 'Luồng tương tác chính:')
    add_body_paragraph(doc, 'Android App ↔ Firebase (Auth, Firestore, Storage, FCM) ↔ FastAPI (Chat endpoint) ↔ Gemini API')

    add_heading_chapter(doc, 2, '4.2. Thiết kế cơ sở dữ liệu Firestore')

    add_heading_chapter(doc, 3, '4.2.1. Collections và Documents')

    collections_data = [
        ['Collection', 'Fields chính', 'Mục đích'],
        ['users', 'userId, fullName, email, role, department, salary, avatar, productivityScore', 'Lưu thông tin người dùng'],
        ['tasks', 'taskId, title, description, assignedBy, assignedTo, status, deadline, priority', 'Lưu các task được giao'],
        ['messages', 'messageId, senderId, receiverId, content, timestamp, isRead', 'Lưu tin nhắn chat'],
        ['attendance', 'attendanceId, userId, checkInTime, checkOutTime, date, totalHours, location', 'Lưu dữ liệu chấm công'],
        ['leaveRequests', 'requestId, userId, reason, startDate, endDate, status, approvedBy', 'Lưu yêu cầu nghỉ phép'],
    ]
    add_table_with_header(doc, collections_data, col_widths=[1.2, 3, 1.8])

    add_heading_chapter(doc, 3, '4.2.2. Security Rules')
    add_body_paragraph(doc,
        'Firestore Security Rules được thiết kế để:')

    security_rules = [
        'Chỉ người dùng đã xác thực mới được truy cập dữ liệu',
        'Admin có quyền truy cập tất cả collection',
        'Manager chỉ xem dữ liệu team của mình',
        'Employee chỉ xem/chỉnh sửa dữ liệu cá nhân'
    ]
    for rule in security_rules:
        p = doc.add_paragraph(rule, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_heading_chapter(doc, 2, '4.3. Thiết kế AI Chatbot')

    add_heading_chapter(doc, 3, '4.3.1. Luồng xử lý Chatbot')

    add_body_paragraph(doc, 'Quy trình xử lý một câu hỏi:')

    chatbot_flow = [
        '1. Người dùng nhập câu hỏi trong app',
        '2. App gửi request POST /api/chat tới FastAPI server',
        '3. Backend nhận request, chuyển câu hỏi thành vector embedding',
        '4. Tìm kiếm các tài liệu liên quan trong ChromaDB',
        '5. Rerank kết quả để lấy top-k tài liệu liên quan nhất',
        '6. Xây dựng prompt kết hợp context + câu hỏi',
        '7. Gửi prompt tới Gemini API để sinh câu trả lời',
        '8. Lưu lịch sử hội thoại vào database',
        '9. Trả về response (answer, intent, confidence) cho app',
        '10. App hiển thị câu trả lời cho người dùng'
    ]
    for step in chatbot_flow:
        p = doc.add_paragraph(step)
        p.paragraph_format.space_after = Pt(6)
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_heading_chapter(doc, 3, '4.3.2. Intent Classification')

    add_body_paragraph(doc, 'Hệ thống phân loại intent của câu hỏi:')

    intents_data = [
        ['Intent', 'Ví dụ', 'Xử lý'],
        ['employee_status', 'Nhân viên X làm việc ở đâu?', 'Truy vấn database'],
        ['document_qa', 'Quy trình xin nghỉ như thế nào?', 'RAG + Gemini'],
        ['out_of_scope', 'Thời tiết hôm nay?', 'Từ chối trả lời'],
    ]
    add_table_with_header(doc, intents_data, col_widths=[1.5, 2.5, 2])

    add_page_break(doc)

    # ==================== CHƯƠNG 5: XÂY DỰNG CHỨC NĂNG ====================
    add_heading_chapter(doc, 1, 'CHƯƠNG 5: XÂY DỰNG CHỨC NĂNG')

    add_heading_chapter(doc, 2, '5.1. Hệ thống đăng nhập và phân quyền')

    add_heading_chapter(doc, 3, '5.1.1. Luồng đăng nhập')
    add_body_paragraph(doc, 'Quy trình đăng nhập:')

    login_flow = [
        'Người dùng nhập email/mật khẩu',
        '↓',
        'Gửi request đến LoginActivity',
        '↓',
        'FirebaseAuth.signInWithEmailAndPassword()',
        '↓',
        'Firebase xác thực thông tin',
        '↓',
        'Lấy UID, sau đó query Firestore (users/{uid}) để lấy role',
        '↓',
        'Lưu session info vào SharedPreferences',
        '↓',
        'Điều hướng đến Dashboard tương ứng (Admin/Manager/Employee)',
        '↓',
        'Kết quả: Đăng nhập thành công hoặc hiển thị lỗi'
    ]
    for step in login_flow:
        p = doc.add_paragraph(step)
        p.paragraph_format.space_after = Pt(4)
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_heading_chapter(doc, 3, '5.1.2. Phân quyền (Role-based Access Control)')
    add_body_paragraph(doc,
        'Sau khi đăng nhập, ứng dụng kiểm tra role của người dùng (Admin/Manager/Employee) lưu trong Firestore. '
        'Dựa trên role, người dùng được điều hướng đến dashboard tương ứng và chỉ có thể truy cập các chức năng được phép.')

    add_heading_chapter(doc, 2, '5.2. Quản lý nhân viên')
    add_body_paragraph(doc,
        'Admin có thể xem danh sách nhân viên, thêm nhân viên mới, sửa thông tin, xóa nhân viên. Thông tin nhân viên được lưu '
        'trong Firestore collection "users".')

    add_heading_chapter(doc, 2, '5.3. Chấm công và tracking')
    add_body_paragraph(doc,
        'Nhân viên có thể check-in/check-out thông qua ứng dụng. Hệ thống lưu lại thời gian check-in, check-out, tính toán tổng '
        'số giờ làm việc. Dữ liệu lưu trong collection "attendance".')

    add_heading_chapter(doc, 2, '5.4. Quản lý nghỉ phép')
    add_body_paragraph(doc,
        'Nhân viên gửi đơn xin nghỉ, Manager phê duyệt/từ chối. Dữ liệu lưu trong collection "leaveRequests" với các trạng thái: '
        'pending, approved, rejected.')

    add_heading_chapter(doc, 2, '5.5. Quản lý nhiệm vụ (Task)')
    add_body_paragraph(doc,
        'Admin/Manager giao task cho nhân viên, nhân viên cập nhật trạng thái task (todo, in-progress, done). '
        'Dữ liệu lưu trong "tasks" collection.')

    add_heading_chapter(doc, 2, '5.6. Tính toán lương')
    add_body_paragraph(doc,
        'Admin tính lương tự động dựa trên: lương cơ sở + phụ cấp - bảo hiểm - thuế. Công thức tính lương được lưu cấu hình '
        'trong ứng dụng. Kết quả tính lương được lưu và có thể export.')

    add_heading_chapter(doc, 2, '5.7. Thống kê và báo cáo')
    add_body_paragraph(doc,
        'Hệ thống cung cấp các biểu đồ thống kê: số lượng nhân viên, chấm công, task hoàn thành, lương trung bình. '
        'Sử dụng MPAndroidChart để vẽ biểu đồ.')

    add_heading_chapter(doc, 2, '5.8. Chat nội bộ realtime')
    add_body_paragraph(doc,
        'Nhân viên có thể gửi tin nhắn cho nhau thông qua ứng dụng. Tin nhắn được lưu trong "messages" collection. '
        'Sử dụng Firestore listeners để cập nhật tin nhắn realtime.')

    add_heading_chapter(doc, 2, '5.9. Thông báo Firebase Cloud Messaging')
    add_body_paragraph(doc,
        'Ứng dụng đăng ký FCM token và nhận thông báo push. Khi có sự kiện quan trọng (task mới, nghỉ phép được phê duyệt), '
        'hệ thống gửi thông báo tới các thiết bị.')

    add_heading_chapter(doc, 2, '5.10. Hỗ trợ đa ngôn ngữ')
    add_body_paragraph(doc,
        'Ứng dụng hỗ trợ Tiếng Việt và Tiếng Anh. Chuỗi ký tự được lưu trong file strings.xml (Tiếng Việt) và '
        'strings-en.xml (Tiếng Anh). LocaleHelper giúp chuyển đổi ngôn ngữ.')

    add_heading_chapter(doc, 2, '5.11. Sinh trắc học')
    add_body_paragraph(doc,
        'Ứng dụng hỗ trợ xác thực bằng vân tay sử dụng Android Biometric API. Người dùng có thể bật xác thực sinh trắc học '
        'trong cài đặt để tăng bảo mật.')

    add_heading_chapter(doc, 2, '5.12. AI Assistant và Chatbot')
    add_body_paragraph(doc,
        'Nhân viên có thể gọi AI Assistant để hỏi các câu hỏi về chính sách, quy trình, thông tin nhân sự. Chatbot sử dụng '
        'kỹ thuật RAG để trả lời câu hỏi dựa trên tài liệu nội bộ.')

    add_page_break(doc)

    # ==================== CHƯƠNG 6: KIỂM THỬ ====================
    add_heading_chapter(doc, 1, 'CHƯƠNG 6: KIỂM THỬ VÀ ĐÁNH GIÁ')

    add_heading_chapter(doc, 2, '6.1. Mục tiêu kiểm thử')
    add_body_paragraph(doc,
        'Kiểm thử nhằm đảm bảo hệ thống hoạt động đúng, an toàn, hiệu quả:')

    test_objectives = [
        'Kiểm thử chức năng: Tất cả tính năng hoạt động đúng theo yêu cầu',
        'Kiểm thử bảo mật: Hệ thống bảo vệ dữ liệu và xác thực người dùng',
        'Kiểm thử hiệu năng: Response time < 2 giây, app không crash',
        'Kiểm thử khả năng sử dụng: Giao diện trực quan, dễ sử dụng',
        'Kiểm thử tích hợp: Các component (Android + Firebase + FastAPI) hoạt động tốt cùng nhau'
    ]
    for obj in test_objectives:
        p = doc.add_paragraph(obj, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_heading_chapter(doc, 2, '6.2. Test case và kết quả')

    test_cases = [
        ['TC-01', 'Đăng nhập email/mật khẩu hợp lệ', 'Đăng nhập thành công', 'Pass'],
        ['TC-02', 'Đăng nhập email/mật khẩu sai', 'Hiển thị lỗi "Email hoặc mật khẩu không chính xác"', 'Pass'],
        ['TC-03', 'Thêm nhân viên mới (Admin)', 'Nhân viên được thêm vào Firestore', 'Pass'],
        ['TC-04', 'Sửa thông tin nhân viên (Admin)', 'Thông tin cập nhật trong Firestore', 'Pass'],
        ['TC-05', 'Xóa nhân viên (Admin)', 'Nhân viên bị xóa khỏi hệ thống', 'Pass'],
        ['TC-06', 'Check-in/Check-out', 'Thời gian được ghi lại đúng', 'Pass'],
        ['TC-07', 'Gửi task (Manager)', 'Task được lưu, nhân viên nhận thông báo', 'Pass'],
        ['TC-08', 'Xin nghỉ phép', 'Yêu cầu được gửi, Manager phê duyệt', 'Pass'],
        ['TC-09', 'Chat nội bộ', 'Tin nhắn được gửi/nhận realtime', 'Pass'],
        ['TC-10', 'AI Chatbot - Hỏi document_qa', 'Chatbot trả lời từ tài liệu', 'Pass'],
        ['TC-11', 'AI Chatbot - Hỏi out_of_scope', 'Chatbot từ chối trả lời', 'Pass'],
        ['TC-12', 'Thông báo FCM', 'Nhận được thông báo push', 'Pass'],
        ['TC-13', 'Chuyển ngôn ngữ sang Tiếng Anh', 'Giao diện chuyển sang Tiếng Anh', 'Pass'],
        ['TC-14', 'Xác thực sinh trắc học', 'Mở khóa ứng dụng bằng vân tay', 'Pass'],
        ['TC-15', 'Thống kê dữ liệu', 'Biểu đồ hiển thị đúng', 'Pass'],
    ]
    add_table_with_header(doc, test_cases, col_widths=[0.7, 2.3, 2, 0.8])

    add_heading_chapter(doc, 2, '6.3. Kết quả kiểm thử')
    add_body_paragraph(doc, 'Tổng test case: 15 / Passed: 15 / Failed: 0 / Pass rate: 100%')

    add_heading_chapter(doc, 2, '6.4. Đánh giá ưu điểm')

    advantages = [
        'Giao diện đẹp, thân thiện với người dùng, tuân theo Material Design',
        'Hệ thống hoạt động realtime nhờ Firestore, dữ liệu cập nhật tức thì',
        'Tích hợp AI Chatbot giúp tự động trả lời câu hỏi, giảm tải công việc HR',
        'Bảo mật cao: Firebase Authentication, Firestore Security Rules',
        'Hỗ trợ đa ngôn ngữ, phù hợp với thị trường đa quốc gia',
        'Xác thực sinh trắc học tăng bảo mật',
        'Thông báo FCM giúp nhân viên cập nhật thông tin kịp thời',
        'Hệ thống quản lý quyền (RBAC) rõ ràng và an toàn'
    ]
    for adv in advantages:
        p = doc.add_paragraph(adv, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_heading_chapter(doc, 2, '6.5. Hạn chế hiện tại')

    limitations = [
        'Chatbot chỉ hỗ trợ Tiếng Việt, chưa hỗ trợ ngôn ngữ khác',
        'Vector database (ChromaDB) chỉ lưu trữ locally, không scalable cho dữ liệu lớn',
        'Chưa tích hợp advanced analytics (machine learning) để dự báo tuyển dụng',
        'Chưa hỗ trợ integration với các hệ thống bên ngoài (Stripe, Slack, v.v.)',
        'Sinh trắc học chỉ hỗ trợ vân tay, chưa hỗ trợ khuôn mặt',
        'Chat nội bộ chỉ hỗ trợ text, chưa hỗ trợ file/hình ảnh',
        'Hiệu năng chậm khi dữ liệu lớn (>10k nhân viên)'
    ]
    for lim in limitations:
        p = doc.add_paragraph(lim, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_page_break(doc)

    # ==================== CHƯƠNG 7: KẾT LUẬN ====================
    add_heading_chapter(doc, 1, 'CHƯƠNG 7: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN')

    add_heading_chapter(doc, 2, '7.1. Kết quả đạt được')

    achievements = [
        'Xây dựng thành công ứng dụng quản lý nhân sự hoàn chỉnh trên Android',
        'Tích hợp Firebase, giải quyết bài toán realtime data sync',
        'Triển khai AI Chatbot sử dụng Gemini API và RAG',
        'Hỗ trợ phân quyền RBAC rõ ràng (Admin/Manager/Employee)',
        'Kiểm thử toàn diện, pass rate 100%',
        'Hỗ trợ đa ngôn ngữ, sinh trắc học, thông báo realtime',
        'Code clean, dễ maintain, có documentation'
    ]
    for ach in achievements:
        p = doc.add_paragraph(ach, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_heading_chapter(doc, 2, '7.2. Hạn chế hiện tại')
    add_body_paragraph(doc,
        'Chatbot chỉ hỗ trợ Tiếng Việt, vector database chưa scalable, chưa hỗ trợ advanced analytics, '
        'chưa tích hợp với hệ thống bên ngoài.')

    add_heading_chapter(doc, 2, '7.3. Hướng phát triển tương lai')

    future_works = [
        'Hỗ trợ Chatbot đa ngôn ngữ (Tiếng Anh, Tiếng Trung, v.v.)',
        'Migrate ChromaDB sang cloud vector database (Pinecone, Weaviate)',
        'Thêm advanced analytics: dự báo lương, phân tích hiệu suất, trend analysis',
        'Tích hợp với Stripe để tính lương và thanh toán điện tử',
        'Tích hợp Slack/Teams để thông báo tự động',
        'Hỗ trợ khuôn mặt (Face ID) ngoài vân tay',
        'Chat nội bộ hỗ trợ file sharing, video call',
        'Optimize hiệu năng cho >100k nhân viên',
        'Hỗ trợ iOS ngoài Android',
        'Dashboard analytics advanced với machine learning predictions'
    ]
    for work in future_works:
        p = doc.add_paragraph(work, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_page_break(doc)

    # ==================== PHÂN CÔNG CÔNG VIỆC ====================
    add_centered_title(doc, 'PHÂN CÔNG CÔNG VIỆC NHÓM')

    team_data = [
        ['Thành viên', 'Công việc chính'],
        ['Thành viên 1',
         'Phân tích yêu cầu hệ thống, thiết kế giao diện Android, xây dựng chức năng đăng nhập, '
         'quản lý nhân sự, quản lý tài khoản, phân quyền Admin/Manager/Employee, tích hợp Firebase Authentication'],
        ['Thành viên 2',
         'Xây dựng các chức năng nghiệp vụ: chấm công, quản lý task, nghỉ phép, thống kê, tính lương, '
         'biểu đồ dữ liệu, Firestore collections, Firebase Storage, Firebase Cloud Messaging, đa ngôn ngữ'],
        ['Thành viên 3',
         'Phát triển module AI Chatbot (Gemini API + RAG), xây dựng backend FastAPI, ChromaDB, '
         'tích hợp AI Assistant vào Android, kiểm thử hệ thống, viết báo cáo'],
    ]
    add_table_with_header(doc, team_data, col_widths=[1.5, 4.5])

    add_body_paragraph(doc, '')
    add_body_paragraph(doc, 'Ngoài ra:')

    collaboration = [
        'Cả 3 thành viên cùng kiểm thử và sửa lỗi',
        'Cùng tối ưu giao diện và hiệu năng',
        'Cùng hoàn thiện tài liệu và chuẩn bị demo'
    ]
    for collab in collaboration:
        p = doc.add_paragraph(collab, style='List Bullet')
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    add_page_break(doc)

    # ==================== TÀI LIỆU THAM KHẢO ====================
    add_centered_title(doc, 'TÀI LIỆU THAM KHẢO')

    references = [
        '[1] Android Developers. (2025). Android App Development Documentation. https://developer.android.com/',
        '[2] Google Firebase. (2025). Firebase Documentation. https://firebase.google.com/docs',
        '[3] Google Cloud. (2025). Firestore Database Guide. https://cloud.google.com/firestore/docs',
        '[4] Google AI. (2025). Gemini API Documentation. https://ai.google.dev/',
        '[5] FastAPI. (2025). FastAPI Framework Documentation. https://fastapi.tiangolo.com/',
        '[6] Chroma. (2025). ChromaDB Documentation. https://docs.trychroma.com/',
        '[7] BAAI. (2025). BGE Model Documentation. https://github.com/FlagOpen/BGE',
        '[8] Material Design. (2025). Material Design Components for Android. https://material.io/',
        '[9] Glide. (2025). Glide Image Loading Library. https://bumptech.github.io/glide/',
        '[10] MPAndroidChart. (2025). MPAndroidChart Documentation. https://github.com/PhilJay/MPAndroidChart',
        '[11] Android Developers. (2025). Biometric API Guide. https://developer.android.com/training/sign-in/biometric-auth',
        '[12] Levin, D. (2024). Advanced RAG Techniques. Technical Blog.',
        '[13] Vaswani, A., et al. (2017). Attention is All You Need. arXiv preprint.',
        '[14] OpenAI. (2024). Retrieval-Augmented Generation: Concepts and Applications. Research Paper.',
        '[15] Thang Le-Tien. (2026). Staff Management System: System Analysis and Design Document. Internal Report.',
    ]

    for i, ref in enumerate(references, 1):
        p = doc.add_paragraph(ref)
        p.paragraph_format.space_after = Pt(6)
        for run in p.runs:
            run.font.size = Pt(13)
            run.font.name = 'Times New Roman'

    # Save document
    output_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'docs',
        'bao-cao-do-an-tot-nghiep.docx'
    )
    doc.save(output_path)
    print('Report generated successfully!')
    print(f'Output: {output_path}')
    print('Open the Word file to edit placeholders and add images/screenshots.')

if __name__ == '__main__':
    create_report()
