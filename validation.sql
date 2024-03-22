with loanlevel AS (
	SELECT ell.distributiondate, 
            ROUND(CAST(SUM(scheduledprincipal) AS numeric),2) AS scheduledprincipal,
            ROUND(CAST(sum(curtailments) AS numeric), 2) AS curtailments,
            ROUND(CAST(sum(prepayment) AS numeric), 2) AS prepayment,	
            ROUND(CAST(sum(repurchaseprincipal) AS numeric), 2) AS repurchaseprincipal,	
            ROUND(CAST(sum(otherprincipaladjustments) AS numeric), 2) AS otherprincipaladjustments
      FROM enhancedloanleveldata ell
      GROUP BY ell.distributiondate)

,totals AS (
      SELECT chs.date
      ,scheduledprincipal
      ,curtailments
      ,prepayment
      ,repurchaseprincipal
      ,otherprincipaladjustments
      ,(scheduledprincipal + curtailments + prepayment + repurchaseprincipal + otherprincipaladjustments) AS total
FROM loanlevel ll
RIGHT JOIN certificate_holders_smt chs
ON chs.date = substring(ll.distributiondate::text, 0, 7)
GROUP BY chs.date, scheduledprincipal,curtailments,prepayment,repurchaseprincipal,otherprincipaladjustments
)

SELECT smt.date
      ,total
      ,total_principal_funds_available
      ,(total-total_principal_funds_available) AS diff
FROM totals t
INNER JOIN certificate_holders_smt smt
ON smt.date=t.date
