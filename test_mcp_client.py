from mcp_client import search_document, list_documents


print("=" * 60)
print("MCP CLIENT TEST")
print("=" * 60)


print("\nAVAILABLE DOCUMENTS")
print("-------------------")

documents = list_documents()

print(documents)


print("\nSEARCH: tobacco")
print("-------------------")

result = search_document("tobacco")

print(result)


print("\nSEARCH: MPOWER")
print("-------------------")

result = search_document("MPOWER")

print(result)


print("\nTEST COMPLETED")