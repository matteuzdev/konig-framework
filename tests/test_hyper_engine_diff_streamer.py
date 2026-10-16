"""
Testes de Bancada e Validação do DiffStreamer & HyperEditEngine (Fase 2).
"""

import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from core.hyper_engine.diff_streamer import DiffStreamer
from core.hyper_engine.edit_engine import HyperEditEngine


def run_tests():
    print("=" * 70)
    print("[KONIG HYPER-ENGINE] - TESTE DE BANCADA DIFF STREAMER (FASE 2)")
    print("=" * 70)

    streamer = DiffStreamer(root_dir=repo_root)

    # 1. Teste de Cálculo de Diff Unificado
    orig_code = (
        "def calculate_tax(amount: float) -> float:\n"
        "    rate = 0.10\n"
        "    return amount * rate\n"
    )
    mod_code = (
        "def calculate_tax(amount: float, is_vip: bool = False) -> float:\n"
        "    rate = 0.05 if is_vip else 0.10\n"
        "    return amount * rate\n"
    )

    diff_res = streamer.compute_diff(orig_code, mod_code, file_path="sample.py")
    print("\n[DIFF COMPUTATION]")
    print(f"  - Linhas adicionadas (+): {diff_res.lines_added}")
    print(f"  - Linhas removidas (-): {diff_res.lines_removed}")
    print(f"  - Hunks detectados: {len(diff_res.hunks)}")

    assert diff_res.lines_added == 2, f"Esperado 2 adições, obteve {diff_res.lines_added}"
    assert diff_res.lines_removed == 2, f"Esperado 2 remoções, obteve {diff_res.lines_removed}"
    assert len(diff_res.hunks) == 1

    # 2. Teste de Visualização Formatada
    formatted_diff = streamer.format_terminal_diff(diff_res, colored=False)
    print("\n[PREVIEW DE DIFF FORMATADO]:")
    print(formatted_diff)
    assert "calculate_tax" in formatted_diff

    # 3. Teste de Aplicação Atômica e Rollback (.undo)
    test_file_rel = "tests/fixtures/test_scratch_target.py"
    test_file_abs = os.path.join(repo_root, test_file_rel)
    os.makedirs(os.path.dirname(test_file_abs), exist_ok=True)

    # Escreve estado inicial
    with open(test_file_abs, "w", encoding="utf-8") as f:
        f.write(orig_code)

    print(f"\n[APLICAÇÃO ATÔMICA EM DISCO: {test_file_rel}]")
    applied = streamer.apply_diff_atomically(test_file_rel, mod_code, make_backup=True)
    assert applied is True

    # Verifica se arquivo no disco contém o novo código
    with open(test_file_abs, "r", encoding="utf-8") as f:
        current_disk_content = f.read()
    assert current_disk_content == mod_code
    print("  - [OK] Arquivo atualizado atomicamente no disco.")

    # Verifica se backup .undo foi criado
    undo_file = f"{test_file_abs}.undo"
    assert os.path.exists(undo_file), "Arquivo de backup .undo deveria existir!"
    print(f"  - [OK] Backup de segurança .undo verificado em: {undo_file}")

    # 4. Teste de Rollback Atômico
    print("\n[ROLLBACK / UNDO]")
    rolled_back = streamer.rollback(test_file_rel)
    assert rolled_back is True

    with open(test_file_abs, "r", encoding="utf-8") as f:
        restored_disk_content = f.read()
    assert restored_disk_content == orig_code
    print("  - [OK] Rollback executado com sucesso: Conteúdo original 100% restaurado.")

    # 5. Teste da Engine CLI (Dry-Run & Auto-Apply)
    print("\n[TESTE DO HYPER-EDIT ENGINE]")
    engine = HyperEditEngine(root_dir=repo_root)

    # Dry-run
    diff_dry, msg_dry = engine.edit(
        file_path=test_file_rel,
        instruction="Adicionar docstring informando taxa padrão de 10%",
        dry_run=True,
    )
    assert "[DRY-RUN]" in msg_dry
    print(f"  - Dry-Run status: {msg_dry}")

    # Limpeza dos fixtures de teste
    if os.path.exists(test_file_abs):
        os.remove(test_file_abs)
    if os.path.exists(undo_file):
        os.remove(undo_file)

    print("\n" + "=" * 70)
    print("[OK] HOMOLOGAÇÃO: DIFF STREAMER & ATOMIC ENGINE PASSARAM COM SUCESSO!")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
