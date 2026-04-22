import pandas as pd
from .models import Process, InventoryItem, EmergyReference

def import_data(file, project):
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    
    # Padroniza apenas o cabeçalho
    df.columns = [c.strip().capitalize() for c in df.columns]
    
    count = 0
    for _, row in df.iterrows():
        try:
            quantity = float(row['Quantity'])
            # .strip() remove espaços em branco antes e depois (essencial!)
            resource_name = str(row['Resource']).strip()
            
            # --- DEBUG NO TERMINAL ---
            print(f"--- Tentando importar: '{resource_name}' ---")
            
            process_name = str(row.get('Process', 'Processo Geral')).strip()
            process, _ = Process.objects.get_or_create(project=project, name=process_name)
            
            # Busca a referência
            ref = EmergyReference.objects.filter(resource_name__iexact=resource_name).first()
            
            if ref:
                uev = ref.uev_value
                print(f"SUCESSO: Encontrei UEV {uev} para {resource_name}")
            else:
                uev = 0.0
                print(f"AVISO: Nao encontrei '{resource_name}' no Banco de Dados (Admin)")

            InventoryItem.objects.create(
                process=process,
                resource_name=resource_name,
                quantity=quantity,
                unit=str(row['Unit']).strip(),
                reference=ref,
                applied_uev=uev,
                calculated_emergy=float(quantity * uev)
            )
            count += 1
        except Exception as e:
            print(f"ERRO NA LINHA: {e}")
            continue
    return count