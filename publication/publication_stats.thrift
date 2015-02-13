exception ValueError {
    1: string message,
}

struct aggs {
    1: string key,
    2: i32 count,
}

struct nested_aggs {
    1: string key,
    2: i32 count,
    3: list<aggs> nested_aggs
}

struct filters {
    1: string param,
    2: string value
}

service PublicationStats {
    list<aggs> journal_subject_areas(1: optional map<string,string> filters) throws (1:ValueError value_err),
    list<nested_aggs> journal_subject_areas_aggs(1:string aggs, 2: optional map<string,string> filters),
    list<aggs> journal_collections(1: optional map<string,string> filters) throws (1:ValueError value_err),
    list<aggs> journal_statuses(1: optional map<string,string> filters) throws (1:ValueError value_err),
    list<aggs> journal_inclusion_years(1: optional map<string,string> filters) throws (1:ValueError value_err),
    list<aggs> document_subject_areas(1: optional map<string,string> filters) throws (1:ValueError value_err),
    list<aggs> document_collections(1: optional map<string,string> filters) throws (1:ValueError value_err),
    list<aggs> document_publication_years(1: optional map<string,string> filters),
    list<aggs> document_languages(1: optional map<string,string> filters) throws (1:ValueError value_err),
    list<aggs> document_affiliation_countries(1: optional map<string,string> filters) throws (1:ValueError value_err),
    list<aggs> document_types(1: optional map<string,string> filters) throws (1:ValueError value_err),
    string query(1: string doc_type, 2: string body) throws (1:ValueError value_err),
}