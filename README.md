# Podobnost hlasov�n� politik�
-----
### Zad�n�:

_Pou�ijte otev�en� data z Poslaneck� sn�movny na adrese [https://www.psp.cz/sqw/hp.sqw?k=1300](https://www.psp.cz/sqw/hp.sqw?k=1300) a z�skejte seznam poslanc�, kte�� jsou aktivn� v tomto volebn�m obdob�. Pro ka�d�ho z nich pomoc� wikipedie, ide�ln� pomoc� jejich profilu na wikidata zjist�te tak� jejich povol�n�. Pokud u n�jak�ho poslance nen� mo�n� dohledat jeho odbornost/p�edchoz� povol�n�, vy�krtn�te ho ze seznamu._

_N�sledn� prove�te anal�zu jejich hlasov�n� a zjist�te, jestli shoda v odbornosti/profesi se projevuje tak� p�i hlasov�n�, nebo jestli je p�i jejich hlasov�n� v�znamn�j�� shoda v r�mci politick� strany. Jin�mi slovy zjist�te, jestli hlasov�n� politika v�ce ovlivn�n� politick� p��slu�nost, nebo odbornost._

_V�ce ne� kvalita datasetu, nebo zkreslen� dan� t�matem hlasov�n� n�s zaj�m� V� p��stup k z�sk�n� dat, jejich propojen� a postup vyhodnocen�. V�slednou pr�ci n�m pros�m po�lete dop�edu v�etn� zdrojov�ho k�du a v druh�m kole prodiskutujeme k �emu jste do�el a jak� postup jste k tomu zvolil._

-----
### Postup:
1. Na�ten� dat z webov�ch str�nek [Poslaneck� sn�movny Parlamentu �esk� republiky](https://www.psp.cz/sqw/hp.sqw?k=1300)
2. Na�ten� �daj� o zam�stn�n� politik� z [wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page).
3. Transformace �daj� o hlasov�n�:
	* pou�it� metody [One-Hot Encoder](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.OneHotEncoder.html) pro transformaci pro / proti / zdr�el se
	* pou�it� [TruncatedSVD](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.TruncatedSVD.html) pro prvn� zredukov�n� dimenzionality na 50
	* pou�it� metody [T-distributed Stochastic Neighbor Embedding](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html) pro fin�ln� zredukov�n� dimenzionality na 2
4. vizualizace podobnosti
-----
# Uk�zka

![](demo.gif)
-----
# TODO

1. Vytvo�it filtr na jednotliv� t�mata hlasov�n�. L�ka�i mohou hlasovat stejn� jako strana, ve kter� jsou �leny pro obecn� t�mata, ale pro l�ka�sk� t�mata mohou hlasovat jednotn�.
2. Pro�istit dataset zam�stn�n� (u�itel, u�itel matematiky, u�itel na vysok� �kole, ...)