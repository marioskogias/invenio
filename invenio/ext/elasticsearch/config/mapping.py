mappings = {
    "records": {
        "properties": {
            "collections": {
                "index": "not_analyzed",
                "type": "string"
            },
            "authors": {
                "type": "nested",
                "properties": {
                    "first_name": {
                        "type": "string"
                    },
                    "last_name": {
                        "type": "string"
                    },
                    "full_name": {
                        "type": "string"
                    }
                }
            }
        }
    }
}

