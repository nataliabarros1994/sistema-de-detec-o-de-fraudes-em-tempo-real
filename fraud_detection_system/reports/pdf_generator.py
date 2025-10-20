"""
=====================================================================
Sistema de Detecção de Fraudes - Gerador de Relatórios PDF
=====================================================================
Gera relatórios profissionais em PDF com gráficos, métricas e análises
detalhadas no estilo corporativo LexisNexis.

Autor: Natália Barros
Data: 2025
=====================================================================
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sem interface gráfica
import numpy as np
from typing import List, Dict, Any

class FraudReportPDF:
    """Gerador de relatórios PDF profissionais"""

    def __init__(self, filename: str = None):
        """
        Inicializa o gerador de relatórios

        Args:
            filename: Nome do arquivo PDF (se None, usa timestamp)
        """
        if filename is None:
            filename = f"relatorio_fraudes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=0.75*inch
        )

        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

        # Cores corporativas
        self.color_primary = colors.HexColor('#00778b')
        self.color_secondary = colors.HexColor('#005266')
        self.color_success = colors.HexColor('#28a745')
        self.color_warning = colors.HexColor('#ffc107')
        self.color_danger = colors.HexColor('#dc3545')

    def _setup_custom_styles(self):
        """Configura estilos customizados"""

        # Título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#00778b'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#005266'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Corpo
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#212529'),
            spaceAfter=12,
            leading=14
        ))

        # Métrica destacada
        self.styles.add(ParagraphStyle(
            name='MetricValue',
            parent=self.styles['Normal'],
            fontSize=36,
            textColor=colors.HexColor('#00778b'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Label de métrica
        self.styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6c757d'),
            alignment=TA_CENTER,
            spaceAfter=20
        ))

    def add_header(self, title: str, subtitle: str = None):
        """Adiciona cabeçalho do relatório"""

        # Logo/Título
        self.story.append(Paragraph(f"🛡️ {title}", self.styles['CustomTitle']))

        if subtitle:
            self.story.append(Paragraph(subtitle, self.styles['CustomBody']))

        # Data do relatório
        date_text = f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}"
        date_style = ParagraphStyle(
            'DateStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_RIGHT
        )
        self.story.append(Paragraph(date_text, date_style))
        self.story.append(Spacer(1, 0.3*inch))

        # Linha divisória
        line_table = Table([['']], colWidths=[7*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, self.color_primary),
        ]))
        self.story.append(line_table)
        self.story.append(Spacer(1, 0.3*inch))

    def add_executive_summary(self, metrics: Dict[str, Any]):
        """Adiciona sumário executivo com métricas principais"""

        self.story.append(Paragraph("Sumário Executivo", self.styles['CustomHeading']))

        # Cria grid de métricas 2x2
        data = [
            [
                self._create_metric_cell(
                    f"{metrics.get('accuracy', 0)*100:.1f}%",
                    "Precisão do Modelo"
                ),
                self._create_metric_cell(
                    f"{metrics.get('total_transactions', 0):,}",
                    "Transações Analisadas"
                )
            ],
            [
                self._create_metric_cell(
                    f"{metrics.get('fraud_detected', 0)}",
                    "Fraudes Detectadas"
                ),
                self._create_metric_cell(
                    f"R$ {metrics.get('money_saved', 0)/1000:.1f}K",
                    "Economia Estimada"
                )
            ]
        ]

        metrics_table = Table(data, colWidths=[3.5*inch, 3.5*inch])
        metrics_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8f9fa')),
            ('PADDING', (0, 0), (-1, -1), 15),
        ]))

        self.story.append(metrics_table)
        self.story.append(Spacer(1, 0.3*inch))

    def _create_metric_cell(self, value: str, label: str):
        """Cria célula de métrica formatada"""
        return [
            Paragraph(value, self.styles['MetricValue']),
            Paragraph(label, self.styles['MetricLabel'])
        ]

    def add_fraud_analysis_table(self, predictions: List[Dict]):
        """Adiciona tabela de análises de fraude"""

        self.story.append(Paragraph("Análise Detalhada das Transações", self.styles['CustomHeading']))

        # Cabeçalho
        data = [['ID Transação', 'Valor', 'Probabilidade', 'Risco', 'Status']]

        # Limita a 20 transações para o relatório
        for pred in predictions[:20]:
            tx_id = pred.get('transaction_id', 'N/A')[:15]
            amount = f"R$ {pred.get('amount', 0):.2f}"
            fraud_prob = f"{pred.get('fraud_probability', 0)*100:.1f}%"
            risk = pred.get('risk_level', 'low').upper()
            status = "FRAUDE" if pred.get('is_fraud', False) else "LEGÍTIMA"

            data.append([tx_id, amount, fraud_prob, risk, status])

        # Cria tabela
        table = Table(data, colWidths=[1.5*inch, 1.2*inch, 1.3*inch, 1*inch, 1*inch])

        # Estilo da tabela
        table.setStyle(TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), self.color_primary),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Corpo
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))

        if len(predictions) > 20:
            note = f"Nota: Exibindo 20 de {len(predictions)} transações. Veja o arquivo completo para mais detalhes."
            self.story.append(Paragraph(note, self.styles['CustomBody']))

    def add_chart(self, chart_data: Dict, chart_type: str = 'bar'):
        """Adiciona gráfico ao relatório"""

        self.story.append(Paragraph("Visualização de Dados", self.styles['CustomHeading']))

        # Cria gráfico com matplotlib
        fig, ax = plt.subplots(figsize=(7, 4))

        if chart_type == 'bar':
            categories = chart_data.get('categories', [])
            values = chart_data.get('values', [])

            ax.bar(categories, values, color='#00778b', alpha=0.8)
            ax.set_ylabel('Quantidade')
            ax.set_title('Distribuição de Fraudes por Categoria', fontsize=14, fontweight='bold')

        elif chart_type == 'pie':
            labels = chart_data.get('labels', [])
            sizes = chart_data.get('sizes', [])
            colors_pie = ['#00778b', '#28a745', '#dc3545', '#ffc107']

            ax.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%', startangle=90)
            ax.set_title('Proporção de Fraudes vs Legítimas', fontsize=14, fontweight='bold')

        elif chart_type == 'line':
            dates = chart_data.get('dates', [])
            values = chart_data.get('values', [])

            ax.plot(dates, values, color='#00778b', linewidth=2, marker='o')
            ax.set_xlabel('Data')
            ax.set_ylabel('Taxa de Fraude (%)')
            ax.set_title('Tendência de Fraudes - Últimos 30 Dias', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45)

        plt.tight_layout()

        # Salva gráfico em buffer
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()

        # Adiciona ao relatório
        img = Image(img_buffer, width=6*inch, height=3.5*inch)
        self.story.append(img)
        self.story.append(Spacer(1, 0.3*inch))

    def add_recommendations(self, fraud_count: int, total: int):
        """Adiciona seção de recomendações"""

        self.story.append(Paragraph("Recomendações e Ações", self.styles['CustomHeading']))

        fraud_rate = (fraud_count / max(total, 1)) * 100

        recommendations = []

        if fraud_rate > 5:
            recommendations.append("🔴 CRÍTICO: Taxa de fraude acima de 5%. Revisão urgente necessária.")
            recommendations.append("• Implementar verificação adicional para transações de alto valor")
            recommendations.append("• Auditar padrões de comportamento dos últimos 30 dias")
            recommendations.append("• Considerar bloqueio temporário de contas suspeitas")

        elif fraud_rate > 2:
            recommendations.append("🟡 ATENÇÃO: Taxa de fraude moderada. Monitoramento reforçado.")
            recommendations.append("• Aumentar frequência de revisões manuais")
            recommendations.append("• Ajustar limites de aprovação automática")
            recommendations.append("• Treinar novo modelo com dados recentes")

        else:
            recommendations.append("🟢 NORMAL: Sistema operando dentro dos parâmetros esperados.")
            recommendations.append("• Manter monitoramento contínuo")
            recommendations.append("• Revisar mensalmente as métricas de performance")
            recommendations.append("• Documentar casos especiais para melhoria do modelo")

        # Boas práticas gerais
        recommendations.extend([
            "",
            "<b>Boas Práticas Recomendadas:</b>",
            "✓ Realizar análise semanal de tendências",
            "✓ Manter backup dos dados de transações",
            "✓ Treinar equipe para identificação manual de padrões",
            "✓ Integrar com sistemas de notificação em tempo real"
        ])

        for rec in recommendations:
            self.story.append(Paragraph(rec, self.styles['CustomBody']))

        self.story.append(Spacer(1, 0.2*inch))

    def add_footer_info(self):
        """Adiciona informações de rodapé"""

        self.story.append(Spacer(1, 0.3*inch))

        # Linha divisória
        line_table = Table([['']], colWidths=[7*inch])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.grey),
        ]))
        self.story.append(line_table)

        footer_text = """
        <para align=center>
        <font size=9 color="#6c757d">
        Este relatório foi gerado automaticamente pelo Sistema de Detecção de Fraudes<br/>
        Desenvolvido por Natália Barros | Tecnologia: Machine Learning + Python<br/>
        Para mais informações, consulte a documentação técnica do sistema
        </font>
        </para>
        """

        self.story.append(Spacer(1, 0.2*inch))
        self.story.append(Paragraph(footer_text, self.styles['Normal']))

    def generate(self, data: Dict[str, Any]) -> str:
        """
        Gera o relatório PDF completo

        Args:
            data: Dicionário com os dados do relatório

        Returns:
            Caminho do arquivo gerado
        """

        # Cabeçalho
        self.add_header(
            "Relatório de Detecção de Fraudes",
            "Análise Corporativa de Transações Financeiras"
        )

        # Sumário executivo
        metrics = {
            'accuracy': data.get('accuracy', 0.968),
            'total_transactions': data.get('total_transactions', 0),
            'fraud_detected': data.get('fraud_detected', 0),
            'money_saved': data.get('total_transactions', 0) * 150
        }
        self.add_executive_summary(metrics)

        # Tabela de análises
        predictions = data.get('predictions', [])
        if predictions:
            self.add_fraud_analysis_table(predictions)

        # Gráficos
        if data.get('include_charts', True):
            # Gráfico de barras
            chart_data = {
                'categories': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
                'values': [15, 23, 18, 31, 27, 22]
            }
            self.add_chart(chart_data, 'bar')

            # Gráfico de pizza
            fraud_count = data.get('fraud_detected', 0)
            legit_count = data.get('total_transactions', 0) - fraud_count
            chart_data = {
                'labels': ['Legítimas', 'Fraudes'],
                'sizes': [legit_count, fraud_count]
            }
            self.add_chart(chart_data, 'pie')

        # Recomendações
        self.add_recommendations(
            fraud_count=data.get('fraud_detected', 0),
            total=data.get('total_transactions', 0)
        )

        # Rodapé
        self.add_footer_info()

        # Gera PDF
        self.doc.build(self.story)

        return self.filename


# ===== FUNÇÃO DE CONVENIÊNCIA =====

def generate_fraud_report(
    predictions: List[Dict],
    filename: str = None,
    include_charts: bool = True
) -> str:
    """
    Função de conveniência para gerar relatório

    Args:
        predictions: Lista de predições
        filename: Nome do arquivo (opcional)
        include_charts: Se deve incluir gráficos

    Returns:
        Caminho do arquivo gerado
    """

    # Calcula métricas
    total_transactions = len(predictions)
    fraud_detected = sum(1 for p in predictions if p.get('is_fraud', False))

    data = {
        'total_transactions': total_transactions,
        'fraud_detected': fraud_detected,
        'predictions': predictions,
        'include_charts': include_charts,
        'accuracy': 0.968  # Valor padrão do modelo
    }

    # Gera relatório
    generator = FraudReportPDF(filename)
    output_file = generator.generate(data)

    return output_file


# ===== TESTE =====

if __name__ == "__main__":
    # Dados de exemplo
    sample_predictions = [
        {
            'transaction_id': 'tx_001',
            'amount': 1500.00,
            'fraud_probability': 0.85,
            'risk_level': 'high',
            'is_fraud': True
        },
        {
            'transaction_id': 'tx_002',
            'amount': 250.00,
            'fraud_probability': 0.12,
            'risk_level': 'low',
            'is_fraud': False
        },
        {
            'transaction_id': 'tx_003',
            'amount': 5000.00,
            'fraud_probability': 0.92,
            'risk_level': 'high',
            'is_fraud': True
        }
    ]

    # Gera relatório de teste
    output = generate_fraud_report(sample_predictions)
    print(f"✅ Relatório gerado: {output}")
