"""
Testes automatizados para o módulo id2json3_optimized.py

Testa todas as funcionalidades principais do módulo otimizado:
- Parsing de arquivos .id
- Extração de IDs de diferentes tipos de registros
- Conversão de campos ISIS para JSON
- Tratamento de subcampos
- Validação de erros e exceções
- Performance e otimizações
"""

import json
import logging
import os
import tempfile
import unittest
from unittest.mock import patch, mock_open

from scielo_migration.scielo_classic_website.iid2json.id2json3_optimized import (
    pids_and_their_records,
    get_doc_records,
    _get_field_value,
    _get_field_items,
    _parse_subfields,
    _parse_field_line,
    _build_record,
    _parse_id_file,
    _group_records_by_id,
    journal_id,
    issue_id,
    article_id,
    get_id_function,
    IssueIdError,
    ArticleIdError,
    RecordParsingError,
    FIELD_PATTERN,
    SUBFIELD_PATTERN,
    ID_PATTERN
)


class TestRegexPatterns(unittest.TestCase):
    """Testa os padrões regex compilados."""
    
    def test_field_pattern(self):
        """Testa FIELD_PATTERN com diferentes formatos de campo."""
        # Casos válidos
        match = FIELD_PATTERN.match("!v002!1414-431X-bjmbr-1414-431X20165409.xml")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "002")
        self.assertEqual(match.group(2), "1414-431X-bjmbr-1414-431X20165409.xml")
        
        match = FIELD_PATTERN.match("!v049!^cAA970^lpt^tBiodiversidade e Conservação")
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "049")
        self.assertEqual(match.group(2), "^cAA970^lpt^tBiodiversidade e Conservação")
        
        # Casos inválidos
        self.assertIsNone(FIELD_PATTERN.match("v002!content"))
        self.assertIsNone(FIELD_PATTERN.match("!002!content"))
        self.assertIsNone(FIELD_PATTERN.match("!vABC!content"))
    
    def test_subfield_pattern(self):
        """Testa SUBFIELD_PATTERN para separação de subcampos."""
        content = "^cAA970^lpt^tBiodiversidade"
        parts = SUBFIELD_PATTERN.split(content)
        expected = ['', 'c', 'AA970', 'l', 'pt', 't', 'Biodiversidade']
        self.assertEqual(parts, expected)
        
        content = "^_New record^len"
        parts = SUBFIELD_PATTERN.split(content)
        expected = ['', '_', 'New record', 'l', 'en']
        self.assertEqual(parts, expected)
    
    def test_id_pattern(self):
        """Testa ID_PATTERN para identificar início de registros."""
        self.assertTrue(ID_PATTERN.match("!ID 000001"))
        self.assertTrue(ID_PATTERN.match("!ID 123456"))
        self.assertTrue(ID_PATTERN.match("!ID    789"))  # Múltiplos espaços
        
        self.assertFalse(ID_PATTERN.match("ID 000001"))
        self.assertFalse(ID_PATTERN.match("!id 000001"))


class TestSubfieldParsing(unittest.TestCase):
    """Testa parsing de subcampos ISIS."""
    
    def test_simple_content(self):
        """Testa conteúdo simples sem subcampos."""
        result = _parse_subfields("Simple content")
        expected = {"_": "Simple content"}
        self.assertEqual(result, expected)
    
    def test_empty_content(self):
        """Testa conteúdo vazio."""
        result = _parse_subfields("")
        expected = {"_": ""}
        self.assertEqual(result, expected)
        
        result = _parse_subfields(None)
        expected = {"_": ""}
        self.assertEqual(result, expected)
    
    def test_subfields_parsing(self):
        """Testa parsing de subcampos complexos."""
        content = "^cAA970^lpt^tBiodiversidade e Conservação"
        result = _parse_subfields(content)
        expected = {
            "c": "AA970",
            "l": "pt", 
            "t": "Biodiversidade e Conservação"
        }
        self.assertEqual(result, expected)
    
    def test_content_without_initial_caret(self):
        """Testa conteúdo que não inicia com ^."""
        content = "New record^len"
        result = _parse_subfields(content)
        expected = {
            "_": "New record",
            "l": "en"
        }
        self.assertEqual(result, expected)
    
    def test_escaped_circumflex(self):
        """Testa tratamento de circunflexo escapado."""
        content = "^tTitle with \\^ symbol^len"
        result = _parse_subfields(content)
        expected = {
            "t": "Title with ^ symbol",
            "l": "en"
        }
        self.assertEqual(result, expected)


class TestFieldAccess(unittest.TestCase):
    """Testa funções de acesso a campos."""
    
    def setUp(self):
        """Configura dados de teste."""
        self.test_data = {
            "v002": [{"_": "1414-431X-bjmbr"}],
            "v012": [{"_": "Article title", "l": "en"}],
            "v049": [
                {"c": "AA970", "l": "pt", "t": "Biodiversidade"},
                {"c": "AA971", "l": "en", "t": "Biodiversity"}
            ],
            "v880": [{"_": "S1414-431X2016000100001"}]
        }
    
    def test_get_field_value_success(self):
        """Testa acesso bem-sucedido a valores de campos."""
        self.assertEqual(_get_field_value(self.test_data, "v002"), "1414-431X-bjmbr")
        self.assertEqual(_get_field_value(self.test_data, "002"), "1414-431X-bjmbr")
        self.assertEqual(_get_field_value(self.test_data, "v880"), "S1414-431X2016000100001")
    
    def test_get_field_value_not_found(self):
        """Testa acesso a campos inexistentes."""
        self.assertIsNone(_get_field_value(self.test_data, "v999"))
        self.assertIsNone(_get_field_value(self.test_data, "999"))
        self.assertIsNone(_get_field_value({}, "v002"))
    
    def test_get_field_items_success(self):
        """Testa obtenção de múltiplos valores de campo."""
        result = _get_field_items(self.test_data, "v049")
        self.assertEqual(len(result), 2)
        self.assertIn("Biodiversidade", result[0])
        self.assertIn("Biodiversity", result[1])
    
    def test_get_field_items_single_value(self):
        """Testa obtenção de campo com valor único."""
        result = _get_field_items(self.test_data, "v002")
        expected = ["1414-431X-bjmbr"]
        self.assertEqual(result, expected)
    
    def test_get_field_items_not_found(self):
        """Testa obtenção de campo inexistente."""
        self.assertIsNone(_get_field_items(self.test_data, "v999"))


class TestFieldLineParsing(unittest.TestCase):
    """Testa parsing de linhas de campo."""
    
    def test_simple_field_line(self):
        """Testa parsing de linha simples."""
        line = "!v002!1414-431X-bjmbr-1414-431X20165409.xml"
        tag, subfields = _parse_field_line(line)
        
        self.assertEqual(tag, "v002")
        self.assertEqual(subfields["_"], "1414-431X-bjmbr-1414-431X20165409.xml")
    
    def test_complex_field_line(self):
        """Testa parsing de linha com subcampos."""
        line = "!v049!^cAA970^lpt^tBiodiversidade e Conservação"
        tag, subfields = _parse_field_line(line)
        
        self.assertEqual(tag, "v049")
        self.assertEqual(subfields["c"], "AA970")
        self.assertEqual(subfields["l"], "pt")
        self.assertEqual(subfields["t"], "Biodiversidade e Conservação")
    
    def test_invalid_field_line(self):
        """Testa parsing de linha inválida."""
        self.assertIsNone(_parse_field_line("invalid line"))
        self.assertIsNone(_parse_field_line(""))
        self.assertIsNone(_parse_field_line("!invalid!content"))


class TestRecordBuilding(unittest.TestCase):
    """Testa construção de registros."""
    
    def test_build_record_simple(self):
        """Testa construção de registro simples."""
        field_data = [
            ("v002", {"_": "1414-431X-bjmbr"}),
            ("v012", {"_": "Article title", "l": "en"})
        ]
        
        record = _build_record(field_data)
        
        self.assertIn("v002", record)
        self.assertIn("v012", record)
        self.assertEqual(record["v002"][0]["_"], "1414-431X-bjmbr")
        self.assertEqual(record["v012"][0]["_"], "Article title")
    
    def test_build_record_multiple_values(self):
        """Testa construção de registro com valores múltiplos."""
        field_data = [
            ("v049", {"c": "AA970", "l": "pt", "t": "Biodiversidade"}),
            ("v049", {"c": "AA971", "l": "en", "t": "Biodiversity"})
        ]
        
        record = _build_record(field_data)
        
        self.assertEqual(len(record["v049"]), 2)
        self.assertEqual(record["v049"][0]["t"], "Biodiversidade")
        self.assertEqual(record["v049"][1]["t"], "Biodiversity")
    
    def test_build_record_empty_data(self):
        """Testa construção com dados vazios."""
        record = _build_record([])
        self.assertEqual(record, {})


class TestIdGeneration(unittest.TestCase):
    """Testa geração de IDs."""
    
    def test_journal_id(self):
        """Testa extração de ID de periódico."""
        data = {"v400": [{"_": "0001-3765"}]}
        result = journal_id(data)
        self.assertEqual(result, "0001-3765")
        
        # Teste com campo ausente
        result = journal_id({})
        self.assertIsNone(result)
    
    def test_issue_id_success(self):
        """Testa geração bem-sucedida de ID de fascículo."""
        data = {
            "v035": [{"_": "0001-3765"}],
            "v036": [{"_": "20160001"}]
        }
        
        result = issue_id(data)
        self.assertEqual(result, "0001-376520160001")
    
    def test_issue_id_with_padding(self):
        """Testa geração de ID com padding."""
        data = {
            "v035": [{"_": "0001-3765"}],
            "v036": [{"_": "20161"}]  # Issue number needs padding
        }
        
        result = issue_id(data)
        self.assertEqual(result, "0001-376520160001")
    
    def test_issue_id_missing_fields(self):
        """Testa erro com campos ausentes."""
        with self.assertRaises(IssueIdError):
            issue_id({"v035": [{"_": "0001-3765"}]})  # Missing v036
        
        with self.assertRaises(IssueIdError):
            issue_id({"v036": [{"_": "20160001"}]})  # Missing v035
    
    def test_issue_id_short_v036(self):
        """Testa erro com v036 muito curto."""
        data = {
            "v035": [{"_": "0001-3765"}],
            "v036": [{"_": "201"}]  # Too short
        }
        
        with self.assertRaises(IssueIdError):
            issue_id(data)
    
    def test_article_id_from_v880(self):
        """Testa geração de ID de artigo a partir do v880."""
        data = {
            "v706": [{"_": "o"}],
            "v880": [{"_": "S1414-431X2016000100001xyz"}]
        }
        
        result = article_id(data)
        self.assertEqual(result, "S1414-431X2016000100001")
    
    def test_article_id_from_v702(self):
        """Testa fallback para v702."""
        data = {
            "v706": [{"_": "o"}],
            "v880": [{"_": "short"}],  # Too short
            "v702": [{"_": "fallback_id"}]
        }
        
        result = article_id(data)
        self.assertEqual(result, "fallback_id")
    
    def test_article_id_issue_type(self):
        """Testa ID de artigo para registro tipo 'i'."""
        data = {
            "v706": [{"_": "i"}],
            "v035": [{"_": "0001-3765"}],
            "v036": [{"_": "20160001"}]
        }
        
        result = article_id(data)
        self.assertEqual(result, "0001-376520160001")
    
    def test_article_id_no_valid_fields(self):
        """Testa erro sem campos válidos."""
        data = {
            "v706": [{"_": "o"}],
            "v880": [{"_": "short"}]  # Too short, no v702
        }
        
        with self.assertRaises(ArticleIdError):
            article_id(data)


class TestIdFunctionSelector(unittest.TestCase):
    """Testa seletor de função de ID."""
    
    def test_get_id_function_title(self):
        """Testa seleção para tipo 'title'."""
        func = get_id_function("title")
        self.assertEqual(func, journal_id)
    
    def test_get_id_function_issue(self):
        """Testa seleção para tipo 'issue'."""
        func = get_id_function("issue")
        self.assertEqual(func, issue_id)
    
    def test_get_id_function_artigo(self):
        """Testa seleção para tipo 'artigo'."""
        func = get_id_function("artigo")
        self.assertEqual(func, article_id)
    
    def test_get_id_function_default(self):
        """Testa fallback para tipo desconhecido."""
        func = get_id_function("unknown")
        self.assertEqual(func, article_id)


class TestFileProcessing(unittest.TestCase):
    """Testa processamento de arquivos .id."""
    
    def create_temp_id_file(self, content):
        """Cria arquivo temporário com conteúdo específico."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='iso-8859-1')
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_parse_single_record(self):
        """Testa parsing de registro único."""
        content = """!ID 000001
!v002!1414-431X-bjmbr-1414-431X20165409.xml
!v012!New record of Blepharicnema splendens^len
"""
        
        temp_file = self.create_temp_id_file(content)
        
        try:
            records = list(_parse_id_file(temp_file))
            self.assertEqual(len(records), 1)
            
            record = records[0]
            self.assertIn("v002", record)
            self.assertIn("v012", record)
            self.assertEqual(record["v002"][0]["_"], "1414-431X-bjmbr-1414-431X20165409.xml")
            self.assertEqual(record["v012"][0]["_"], "New record of Blepharicnema splendens")
            self.assertEqual(record["v012"][0]["l"], "en")
            
        finally:
            os.unlink(temp_file)
    
    def test_parse_multiple_records(self):
        """Testa parsing de múltiplos registros."""
        content = """!ID 000001
!v002!first-record
!v012!First Record Title

!ID 000002
!v002!second-record
!v012!Second Record Title
"""
        
        temp_file = self.create_temp_id_file(content)
        
        try:
            records = list(_parse_id_file(temp_file))
            self.assertEqual(len(records), 2)
            
            self.assertEqual(records[0]["v002"][0]["_"], "first-record")
            self.assertEqual(records[1]["v002"][0]["_"], "second-record")
            
        finally:
            os.unlink(temp_file)
    
    def test_parse_nonexistent_file(self):
        """Testa parsing de arquivo inexistente."""
        records = list(_parse_id_file("/nonexistent/file.id"))
        self.assertEqual(records, [])
    
    @patch('builtins.open', mock_open(read_data="invalid content"))
    def test_parse_invalid_content(self):
        """Testa parsing de conteúdo inválido."""
        with patch('logging.warning'):
            records = list(_parse_id_file("dummy_file.id"))
            self.assertEqual(records, [])


class TestPidsAndRecords(unittest.TestCase):
    """Testa função principal pids_and_their_records."""
    
    def create_test_file(self):
        """Cria arquivo de teste."""
        content = """!ID 000001
!v035!0001-3765
!v036!20160001
!v706!i

!ID 000002
!v035!0001-3765
!v036!20160001
!v706!i
"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='iso-8859-1')
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_pids_and_records_empty_path(self):
        """Testa com caminho vazio."""
        result = pids_and_their_records("", "issue")
        self.assertEqual(result, [])
        
        result = pids_and_their_records(None, "issue")
        self.assertEqual(result, [])
    
    def test_pids_and_records_success(self):
        """Testa processamento bem-sucedido."""
        temp_file = self.create_test_file()
        
        try:
            with patch('logging.info'):
                result = pids_and_their_records(temp_file, "issue")
                
            self.assertEqual(len(result), 1)  # Same ID for both records
            pid, records = result[0]
            self.assertEqual(pid, "0001-376520160001")
            self.assertEqual(len(records), 2)
            
        finally:
            os.unlink(temp_file)


class TestDocRecords(unittest.TestCase):
    """Testa função get_doc_records."""
    
    def create_doc_test_file(self):
        """Cria arquivo de teste com diferentes tipos de registros."""
        content = """!ID 000001
!v035!0001-3765
!v036!20160001
!v706!i

!ID 000002
!v880!S1414-431X2016000100001
!v706!o
"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='iso-8859-1')
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def test_get_doc_records_issue_type(self):
        """Testa processamento de registro tipo 'i'."""
        temp_file = self.create_doc_test_file()
        
        try:
            with patch('logging.info'):
                docs = list(get_doc_records(temp_file))
            
            # Encontra registro de issue
            issue_doc = next((d for d in docs if 'issue_id' in d), None)
            self.assertIsNotNone(issue_doc)
            self.assertEqual(issue_doc['issue_id'], "0001-376520160001")
            
        finally:
            os.unlink(temp_file)
    
    def test_get_doc_records_article_type(self):
        """Testa processamento de registro tipo 'o'."""
        temp_file = self.create_doc_test_file()
        
        try:
            with patch('logging.info'):
                docs = list(get_doc_records(temp_file))
            
            # Encontra registro de artigo
            article_doc = next((d for d in docs if 'doc_id' in d), None)
            self.assertIsNotNone(article_doc)
            self.assertEqual(article_doc['doc_id'], "S1414-431X2016000100001")
            self.assertEqual(article_doc['i_id'], "1414-431X20160001")
            
        finally:
            os.unlink(temp_file)


class TestPerformanceOptimizations(unittest.TestCase):
    """Testa aspectos de performance e otimizações."""
    
    def test_generator_memory_efficiency(self):
        """Testa que funções retornam generators para eficiência de memória."""
        # Mock file content
        with patch('builtins.open', mock_open(read_data="!ID 001\n!v002!test\n")):
            
            # _parse_id_file deve retornar generator
            result = _parse_id_file("dummy.id")
            self.assertTrue(hasattr(result, '__iter__'))
            self.assertTrue(hasattr(result, '__next__'))
            
            # get_doc_records deve retornar generator
            result = get_doc_records("dummy.id")
            self.assertTrue(hasattr(result, '__iter__'))
            self.assertTrue(hasattr(result, '__next__'))
    
    def test_eafp_pattern_field_access(self):
        """Testa que acesso a campos usa padrão EAFP (try/except)."""
        # Testa que não há KeyError não tratado
        result = _get_field_value({}, "v999")
        self.assertIsNone(result)
        
        # Testa com dados inválidos
        result = _get_field_value({"v999": "invalid"}, "v999")
        self.assertIsNone(result)
    
    def test_regex_compilation_efficiency(self):
        """Testa que regex patterns estão compilados."""
        # Verifica que os patterns são objetos compilados
        self.assertTrue(hasattr(FIELD_PATTERN, 'match'))
        self.assertTrue(hasattr(SUBFIELD_PATTERN, 'split'))
        self.assertTrue(hasattr(ID_PATTERN, 'match'))


class TestErrorHandling(unittest.TestCase):
    """Testa tratamento de erros."""
    
    def test_custom_exceptions(self):
        """Testa exceções customizadas."""
        # Testa IssueIdError
        with self.assertRaises(IssueIdError):
            raise IssueIdError("Test issue error")
        
        # Testa ArticleIdError  
        with self.assertRaises(ArticleIdError):
            raise ArticleIdError("Test article error")
        
        # Testa RecordParsingError
        with self.assertRaises(RecordParsingError):
            raise RecordParsingError("Test parsing error")
    
    def test_graceful_error_handling(self):
        """Testa que erros são tratados graciosamente."""
        # Teste com dados corrompidos
        with patch('logging.warning'):
            result = _get_field_value(None, "v002")
            self.assertIsNone(result)
    
    @patch('logging.warning')
    def test_logging_on_errors(self, mock_logging):
        """Testa que erros são logados apropriadamente."""
        # Força um erro na geração de ID
        with patch('scielo_migration.scielo_classic_website.iid2json.id2json3_optimized._get_field_value', 
                   side_effect=Exception("Test error")):
            
            records = [{"v706": [{"_": "o"}]}]
            result = list(_group_records_by_id(iter(records), article_id))
            
            # Verifica que o warning foi chamado
            mock_logging.assert_called()


if __name__ == '__main__':
    # Configura logging para testes
    logging.basicConfig(level=logging.WARNING)
    
    # Executa testes
    unittest.main(verbosity=2)