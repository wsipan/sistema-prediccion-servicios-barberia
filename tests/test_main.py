from barberia.main import main


def test_main_prints_project_status(capsys):
    main()
    captured = capsys.readouterr()
    assert "predicción de servicios" in captured.out.lower()
    assert "dataset" in captured.out.lower()
