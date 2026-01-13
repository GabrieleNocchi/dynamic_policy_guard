# dynamic_policy_guard
Progettare e implementare "Dynamic Policy Guard", un microservizio HTTP che disaccoppia la logica di business (il codice) dalla logica di policy (i dati). Il sistema deve decidere come redigere un dato basandosi sul recupero semantico (Retrieval) delle regole da un corpus di documenti, simulando un’architettura RAG (Retrieval-Augmented Generation/Execution).



```bash
git clone https://github.com/GabrieleNocchi/dynamic_policy_guard.git
cd dynamic_policy_guard
conda create -n test_env python=3.10
conda activate test_env
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Go to: <a href="http://127.0.0.1:8000/docs" target="_blank">http://127.0.0.1:8000/docs</a>




Per provare Ednpoint /redact usa un Json in questo formato:

```
{
  "customer_id": "beta",
  "policy_version": "",
  "content": {
    "text": "L'utente Mario Rossi (mario@acme.com) ha chiamato il 333-123456.",
    "entities": [
      {
        "type": "NAME",
        "value": "Mario Rossi",
        "start": 9,
        "end": 20
      },
      {
        "type": "EMAIL",
        "value": "mario@acme.com",
        "start": 22,
        "end": 36
      },
      {
        "type": "PHONE",
        "value": "333-123456",
        "start": 53,
        "end": 63
      }
    ]
  }
}

```

Per provare Endpoint /policy/explain usa un JSON in questo formato:

```
{
  "customer_id": "BETA",
  "policy_version": "",
  "entity_type": "PHONE"
}

```
### NOTE: policy_version è opzionale in entrambi gli endpoint (puoi ladciarlo vuoto).

### unit test
```
cd tests
pytest test_retriever.py
```

### notebook test
```
cd notebooks
jupyter notebook
```



#### Comments

Ho cercato di fare questo esercizio senza modificare minimamente le policy.  
La soluzione migliore sarebbe probabilmente che le policy rispettassero un formato standard, ad esempio JSON, ma così com’è la situazione presenta alcune difficoltà:

- La definizione delle azioni (`ACTIONS`) si trova nella POL-GLOBAL policy (non dovrebbe essere dentro NESSUNA policy).  
- Non sembra esserci un criterio solido per creare i chunk (ad esempio per riga), quindi l’aggiunta di nuove policy potrebbe rompere la logica che ho usato a seconda di come sono scritte.  

Per il chunking e retrieval ho adottato questa strategia:  
1. Divido il testo delle policy ogni volta che viene trovata una `ACTION`. Questo perché nelle policy le frasi seguono il formato:  
   - `ENTITY + ACTION` (es. "Le EMAIL devono essere convertite usando HASH per permettere analisi anonime.") oppure  
   -  solo `ACTION` (es. `"Tutto deve essere REDACT"`).  
2. Cerco un chunk che contenga sia l’entity che l’azione richiesta.  
3. Se non esiste, cerco un chunk con solo un’azione (MA senza altre entity) e uso quella.  
4. Durante la creazione delle policy, elimino le linee dove compare `ACTION:` per rimuovere le definizioni dentro POL-GLOBAL ed escluderle dal chunking.  

Questo approccio si rompe se il formato della policy cambia.  
Ad esempio, per la policy BETA:  
 
> "Politica per BETA Inc. Siamo in un settore altamente regolamentato. Tutto deve essere REDACT, eccetto i PHONE che devono essere KEEP per esigenze di contatto urgenti."

Se venisse cambiata in: 
> "Politica per BETA Inc. Siamo in un settore altamente regolamentato. Tutto deve essere REDACT, ma fai KEEP sui PHONE"

Si rompe perchè la policy viene scritta con `ACTION + ENTITY` invece che `ENTITY + ACTION`.  Questo porterebbe due chunk con solo azione (uno con REDACT, uno con KEEP, e un chunk con PHONE), e non funzionerebbe.

In sintesi, il vero problema qui è il chunking a causa delle policy scritte senza rispettare un formato preciso. 

Per il resto:  
- Il codice è modulare, credo abbastanza self-explanatory dai nomi degli script.  
- Ho usato `sentence-transformers` per il modello: non è un vero RAG, ma una ricerca semantica semplice, quindi basta quello. Inoltre era consigliato nelle istruzioni.  
- Nessun DB: ho utilizzato array NumPy.  

Vantaggi di numpy array:  
- Velocità e semplicità: è possibile generare vettori anche casuali o lineari per testare ranking, top_k e filtraggio. Tanto ho solo 3 policy e quindi pochissimi chunks, va bene in memoria.  
- Deterministico: puoi prevedere quale chunk sarà “più rilevante”.  
- Nessuna dipendenza esterna: tutto resta in memoria.  



Ho aggiunto anche l'azione extra per fare vedere che è semplice aggiungere azioni nuove.



Nota finale: questo esercizio è per developers, non per data scientists. Comunque, mi sono divertito e credo di aver imparato qualcosa.


