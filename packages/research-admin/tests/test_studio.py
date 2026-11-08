import re

from fastapi.testclient import TestClient

from research_admin.app import create_app
from research_admin.config import Settings


def test_audience_csv_escapes_spreadsheet_formulas(tmp_path):
    class Vault:
        def get(self):
            return "token"

        def set(self, value):
            pass

        def delete(self):
            pass

    app = create_app(Settings(admin_password="admin-pass", db_path=str(tmp_path / "csv.db")), vault_factory=Vault)
    with TestClient(app, headers={"Origin": "http://testserver"}) as client:
        page = client.get("/login")
        csrf = re.search(r'name=csrf value="([^"]+)', page.text).group(1)
        client.post("/login", data={"password": "admin-pass", "csrf": csrf}, follow_redirects=False)
        app.state.store.save_insights([{"id": 1, "theme": "Trust", "quote": "=CMD()", "source_url": "https://www.threads.com/post/1", "ebook_idea": "A workbook"}])
        export = client.get("/audiences/export.csv")
        assert export.status_code == 200
        assert "'=CMD()" in export.text
