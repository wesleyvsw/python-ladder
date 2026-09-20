from datetime import datetime, timezone
from .constantes import VERSAO_TIA


def _cabecalho_documento() -> str:
    """Abertura comum a todo XML exportado pelo TIA (bloco e tabela de tags)."""
    data = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return f"""<?xml version="1.0" encoding="utf-8"?>
<Document>
  <Engineering version="{VERSAO_TIA}" />
  <DocumentInfo>
    <Created>{data}</Created>
    <ExportSetting>None</ExportSetting>
    <InstalledProducts>
      <Product>
        <DisplayName>Totally Integrated Automation Portal</DisplayName>
        <DisplayVersion>{VERSAO_TIA}</DisplayVersion>
      </Product>
      <OptionPackage>
        <DisplayName>TIA Portal Openness</DisplayName>
        <DisplayVersion>{VERSAO_TIA}</DisplayVersion>
      </OptionPackage>
      <OptionPackage>
        <DisplayName>TIA Portal Version Control Interface</DisplayName>
        <DisplayVersion>{VERSAO_TIA}</DisplayVersion>
      </OptionPackage>
      <Product>
        <DisplayName>STEP 7 Professional</DisplayName>
        <DisplayVersion>{VERSAO_TIA}</DisplayVersion>
      </Product>
      <OptionPackage>
        <DisplayName>STEP 7 Safety</DisplayName>
        <DisplayVersion>{VERSAO_TIA}</DisplayVersion>
      </OptionPackage>
      <Product>
        <DisplayName>WinCC Professional</DisplayName>
        <DisplayVersion>{VERSAO_TIA}</DisplayVersion>
      </Product>
    </InstalledProducts>
  </DocumentInfo>
"""
