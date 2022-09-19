import streamlit as st
import pandas as pd
st.title('References')

st.markdown('Full Python code availble on [GitHub]()')

#st.markdown('#### Sites with > 10 procedures nationally:')
national_provider_filename = 'valve_providers.csv'
#activity_data_filename = "Cardiac valves_national v0.2.csv"
activity_data_minimal_filename = "activity_data_minimal.csv"
procedure_ref = "opcs_table.csv"


def get_national_providers_list(national_provider_filename, activity_data_minimal_filename) :
    df_prov = pd.read_csv(national_provider_filename)
    df_activity = pd.read_csv(activity_data_minimal_filename)
    df_count = df_activity['Der_Provider_Site_Code'].value_counts()
    prov_code_list = df_count[df_count > 10]
    nat_prov10 = df_prov[df_prov['Provider_Site_Code'].isin(list(prov_code_list.index))]
    return nat_prov10


df_opcs = pd.read_csv(procedure_ref)
with st.expander("Cardiac valve procedures list", 
                 expanded=False) :
    st.write(df_opcs)

with st.expander("Sites with > 10 procedures nationally", 
                 expanded=False) :
    st.write(get_national_providers_list(national_provider_filename, 
                                     activity_data_minimal_filename))

with st.expander("SQL used on SUS spells data held by the NCDR",
                 expanded=False) :
    st.code("""
              -- Run 18/03/2022 after re-upload of LSOA reference table folllowing Routino update with Papworth fix
 -- Also addition site code fixes on RK900, RAE00, RAJ00, RYJ00

IF OBJECT_ID('tempdb..#TEMP') IS NOT NULL
                DROP TABLE #TEMP;

IF OBJECT_ID('tempdb..#TEMP1') IS NOT NULL
                DROP TABLE #TEMP1;


IF OBJECT_ID('tempdb..#Time') IS NOT NULL
                DROP TABLE #time;

SELECT DISTINCT
CASE WHEN to_postcode like '%CB2%0AA%' then 'CB20AY' ELSE replace(to_postcode,' ','') END as to_postcode
--replace(to_postcode,' ','') as to_postcode
,replace([from_postcode],' ','') as [from_postcode]
,[distance_km]
,[time_min] 
into #time
FROM NHSE_Sandbox_DC.[dbo].[LSOA_to_site_travel_times] ;

SELECT apcs.Generated_Record_ID 
,der_procedure_all
INTO #TEMP
FROM [NHSE_SUSPlus_Live].[dbo].[tbl_Data_SEM_APCS] apcs
left JOIN NHSE_Reference.[dbo].[tbl_Ref_ODS_Commissioner_Hierarchies] rg
	ON apcs.Der_Postcode_CCG_Code = rg.Organisation_Code
where apcs.Der_Activity_Month >= 201604
and rg.Region_Name IN ('SOUTH EAST','SOUTH WEST','LONDON','MIDLANDS','EAST OF ENGLAND','NORTH EAST AND YORKSHIRE','NORTH WEST')
and apcs.Admission_Method like '1%';


SELECT 
Generated_Record_ID
into #temp1
FROM #temp
WHERE
( --TAVI
	der_procedure_all like '%||K262%' and  (Der_Procedure_All like '%Y494%'
	or Der_Procedure_All like '%Y531%'
    or Der_Procedure_All like '%Y532%'
	or Der_Procedure_All like '%Y533%'															or Der_Procedure_All like '%Y534%'
	or Der_Procedure_All like '%Y535%'
	or Der_Procedure_All like '%Y536%'
	or Der_Procedure_All like '%Y537%'
	or Der_Procedure_All like '%Y538%'
	or Der_Procedure_All like '%Y539%'
	or Der_Procedure_All like '%Y791%'
	or Der_Procedure_All like '%Y792%'
	or Der_Procedure_All like '%Y793%'
	or Der_Procedure_All like '%Y794%'
	or Der_Procedure_All like '%Y798%'
	or Der_Procedure_All like '%Y799%'))
   or
  --AVR
  (Der_Procedure_All like '%K261%'
	or Der_Procedure_All like '%K262%'
	or Der_Procedure_All like '%K263%'
	or Der_Procedure_All like '%K264%'
	or Der_Procedure_All like '%K265%'
	or Der_Procedure_All like '%K268%'
	or Der_Procedure_All like '%K269%'
	or Der_Procedure_All like '%K302%'
	or Der_Procedure_All like '%K312%'
	or Der_Procedure_All like '%K322%')
	
   or
   -- Cardiac surgery valves
	(   der_procedure_all like '%||K251%'
	or der_procedure_all like '%||K252%'
	or der_procedure_all like '%||K253%'
	or der_procedure_all like '%||K254%'
	or der_procedure_all like '%||K255%'
	or der_procedure_all like '%||K258%'
	or der_procedure_all like '%||K259%'
	or der_procedure_all like '%||K271%'
	or der_procedure_all like '%||K272%'
	or der_procedure_all like '%||K273%'
	or der_procedure_all like '%||K274%'
	or der_procedure_all like '%||K275%'
	or der_procedure_all like '%||K276%'
	or der_procedure_all like '%||K278%'
	or der_procedure_all like '%||K279%'
	or der_procedure_all like '%||K281%'
	or der_procedure_all like '%||K282%'
	or der_procedure_all like '%||K283%'
	or der_procedure_all like '%||K284%'
	or der_procedure_all like '%||K285%'
	or der_procedure_all like '%||K288%'
	or der_procedure_all like '%||K289%'
	or der_procedure_all like '%||K291%'
	or der_procedure_all like '%||K292%'
	or der_procedure_all like '%||K293%'
	or der_procedure_all like '%||K294%'
	or der_procedure_all like '%||K295%'
	or der_procedure_all like '%||K296%'
	or der_procedure_all like '%||K297%'
	or der_procedure_all like '%||K298%'
	or der_procedure_all like '%||K299%'
	or der_procedure_all like '%||K301%'
	or der_procedure_all like '%||K303%'
	or der_procedure_all like '%||K304%'
	or der_procedure_all like '%||K305%'
	or der_procedure_all like '%||K308%'
	or der_procedure_all like '%||K309%'
	or der_procedure_all like '%||K311%'
	or der_procedure_all like '%||K313%'
	or der_procedure_all like '%||K314%'
	or der_procedure_all like '%||K315%'
	or der_procedure_all like '%||K318%'
	or der_procedure_all like '%||K319%'
	or der_procedure_all like '%||K321%'
	or der_procedure_all like '%||K323%'
	or der_procedure_all like '%||K324%'
	or der_procedure_all like '%||K328%'
	or der_procedure_all like '%||K329%'
	or der_procedure_all like '%||K331%'
	or der_procedure_all like '%||K332%'
	or der_procedure_all like '%||K333%'
	or der_procedure_all like '%||K334%'
	or der_procedure_all like '%||K335%'
	or der_procedure_all like '%||K336%'
	or der_procedure_all like '%||K338%'
	or der_procedure_all like '%||K339%'
	or der_procedure_all like '%||K341%'
	or der_procedure_all like '%||K342%'
	or der_procedure_all like '%||K343%'
	or der_procedure_all like '%||K344%'
	or der_procedure_all like '%||K345%'
	or der_procedure_all like '%||K346%'
	or der_procedure_all like '%||K348%'
	or der_procedure_all like '%||K349%'
	or der_procedure_all like '%||K358%'
	or der_procedure_all like '%||K359%'
	or der_procedure_all like '%||K361%'
	or der_procedure_all like '%||K362%'
	or der_procedure_all like '%||K368%'
	or der_procedure_all like '%||K369%'
	or der_procedure_all like '%||K371%'
	or der_procedure_all like '%||K372%'
	or der_procedure_all like '%||K373%'
	or der_procedure_all like '%||K374%'
	or der_procedure_all like '%||K375%'
	or der_procedure_all like '%||K376%'
	or der_procedure_all like '%||K378%'
	or der_procedure_all like '%||K379%'
	or der_procedure_all like '%||K381%'
	or der_procedure_all like '%||K382%'
	or der_procedure_all like '%||K383%'
	or der_procedure_all like '%||K384%'
	or der_procedure_all like '%||K385%'
	or der_procedure_all like '%||K386%'
	or der_procedure_all like '%||K388%'
	or der_procedure_all like '%||K389%')
	;


select apcs.APCS_Ident
,apcs.der_financial_year
,apcs.Der_Activity_Month
,Admission_Date
,Admission_Method
,apcs.Age_At_CDS_Activity_Date as Age
,apcs.Der_Provider_Code
,apcs.Der_Provider_Site_Code
,der.NCBFinal_Spell_ServiceLine as Service_Line
,Service_Line_Desc
,substring(apcs.der_procedure_all, 3,4) as Dominant_Procedure_Code
,apcs.Der_Procedure_All
,opcs.OPCS_L4_Desc as Procedure_desc
,case when (apcs.der_procedure_all like '%||K262%' and  (Der_Procedure_All like '%Y494%'
    or Der_Procedure_All like '%Y531%'
	or Der_Procedure_All like '%Y532%'
	or Der_Procedure_All like '%Y533%'
	or Der_Procedure_All like '%Y534%'
	or Der_Procedure_All like '%Y535%'
	or Der_Procedure_All like '%Y536%'
	or Der_Procedure_All like '%Y537%'
	or Der_Procedure_All like '%Y538%'
	or Der_Procedure_All like '%Y539%'
	or Der_Procedure_All like '%Y791%'
	or Der_Procedure_All like '%Y792%'
	or Der_Procedure_All like '%Y793%'
	or Der_Procedure_All like '%Y794%'
	or Der_Procedure_All like '%Y798%'
	or Der_Procedure_All like '%Y799%')) then 'TAVI'
	  when  (Der_Procedure_All like '%K261%'
			or Der_Procedure_All like '%K262%'
			or Der_Procedure_All like '%K263%'
			or Der_Procedure_All like '%K264%'
			or Der_Procedure_All like '%K265%'
			or Der_Procedure_All like '%K268%'
			or Der_Procedure_All like '%K269%'
			or Der_Procedure_All like '%K302%'
			or Der_Procedure_All like '%K312%'
			or Der_Procedure_All like '%K322%') then 'AVR'

	  when (   apcs.der_procedure_all like '%||K251%'
	or apcs.der_procedure_all like '%||K252%'
	or apcs.der_procedure_all like '%||K253%'
	or apcs.der_procedure_all like '%||K254%'
	or apcs.der_procedure_all like '%||K255%'
	or apcs.der_procedure_all like '%||K258%'
	or apcs.der_procedure_all like '%||K259%'
	or apcs.der_procedure_all like '%||K271%'
	or apcs.der_procedure_all like '%||K272%'
	or apcs.der_procedure_all like '%||K273%'
	or apcs.der_procedure_all like '%||K274%'
	or apcs.der_procedure_all like '%||K275%'
	or apcs.der_procedure_all like '%||K276%'
	or apcs.der_procedure_all like '%||K278%'
	or apcs.der_procedure_all like '%||K279%'
	or apcs.der_procedure_all like '%||K281%'
	or apcs.der_procedure_all like '%||K282%'
	or apcs.der_procedure_all like '%||K283%'
	or apcs.der_procedure_all like '%||K284%'
	or apcs.der_procedure_all like '%||K285%'
	or apcs.der_procedure_all like '%||K288%'
	or apcs.der_procedure_all like '%||K289%'
	or apcs.der_procedure_all like '%||K291%'
	or apcs.der_procedure_all like '%||K292%'
	or apcs.der_procedure_all like '%||K293%'
	or apcs.der_procedure_all like '%||K294%'
	or apcs.der_procedure_all like '%||K295%'
	or apcs.der_procedure_all like '%||K296%'
	or apcs.der_procedure_all like '%||K297%'
	or apcs.der_procedure_all like '%||K298%'
	or apcs.der_procedure_all like '%||K299%'
	or apcs.der_procedure_all like '%||K301%'
	or apcs.der_procedure_all like '%||K303%'
	or apcs.der_procedure_all like '%||K304%'
	or apcs.der_procedure_all like '%||K305%'
	or apcs.der_procedure_all like '%||K308%'
	or apcs.der_procedure_all like '%||K309%'
	or apcs.der_procedure_all like '%||K311%'
	or apcs.der_procedure_all like '%||K313%'
	or apcs.der_procedure_all like '%||K314%'
	or apcs.der_procedure_all like '%||K315%'
	or apcs.der_procedure_all like '%||K318%'
	or apcs.der_procedure_all like '%||K319%'
	or apcs.der_procedure_all like '%||K321%'
	or apcs.der_procedure_all like '%||K323%'
	or apcs.der_procedure_all like '%||K324%'
	or apcs.der_procedure_all like '%||K328%'
	or apcs.der_procedure_all like '%||K329%'
	or apcs.der_procedure_all like '%||K331%'
	or apcs.der_procedure_all like '%||K332%'
	or apcs.der_procedure_all like '%||K333%'
	or apcs.der_procedure_all like '%||K334%'
	or apcs.der_procedure_all like '%||K335%'
	or apcs.der_procedure_all like '%||K336%'
	or apcs.der_procedure_all like '%||K338%'
	or apcs.der_procedure_all like '%||K339%'
	or apcs.der_procedure_all like '%||K341%'
	or apcs.der_procedure_all like '%||K342%'
	or apcs.der_procedure_all like '%||K343%'
	or apcs.der_procedure_all like '%||K344%'
	or apcs.der_procedure_all like '%||K345%'
	or apcs.der_procedure_all like '%||K346%'
	or apcs.der_procedure_all like '%||K348%'
	or apcs.der_procedure_all like '%||K349%'
	or apcs.der_procedure_all like '%||K358%'
	or apcs.der_procedure_all like '%||K359%'
	or apcs.der_procedure_all like '%||K361%'
	or apcs.der_procedure_all like '%||K362%'
	or apcs.der_procedure_all like '%||K368%'
	or apcs.der_procedure_all like '%||K369%'
	or apcs.der_procedure_all like '%||K371%'
	or apcs.der_procedure_all like '%||K372%'
	or apcs.der_procedure_all like '%||K373%'
	or apcs.der_procedure_all like '%||K374%'
	or apcs.der_procedure_all like '%||K375%'
	or apcs.der_procedure_all like '%||K376%'
	or apcs.der_procedure_all like '%||K378%'
	or apcs.der_procedure_all like '%||K379%'
	or apcs.der_procedure_all like '%||K381%'
	or apcs.der_procedure_all like '%||K382%'
	or apcs.der_procedure_all like '%||K383%'
	or apcs.der_procedure_all like '%||K384%'
	or apcs.der_procedure_all like '%||K385%'
	or apcs.der_procedure_all like '%||K386%'
	or apcs.der_procedure_all like '%||K388%'
	or apcs.der_procedure_all like '%||K389%') then 'Cardiac Valve Procedure'
	 end as Procedure_Group
,prov.Region_Name as Provider_Region
,rg.Region_Name as Pt_Region
,rg.STP_Code as Pt_STP_Code
,rg.stp_name AS Pt_STP
,apcs.Der_Postcode_LSOA_2011_Code as Patient_LSOA
,time.[distance_km] as Travel_distance_km
,time.[time_min] as Travel_time
,APCS.[Age_At_CDS_Activity_Date] AS Age
,APCS.[Duration_of_Elective_Wait]
,APCS.[Der_Spell_LoS] AS [Length of stay]
,APCS.[Der_Procedure_Count] AS [Procedure count]

FROM #TEMP1 t
inner join [NHSE_SUSPlus_Live].[dbo].[tbl_Data_SEM_APCS] APCS
	on t.Generated_Record_ID  = apcs.Generated_Record_ID 
left JOIN [NHSE_SUSPlus_Live].[dbo].[tbl_Data_SEM_APCS_2122_Der] der
	ON apcs.apcs_ident = der.apcs_ident
left JOIN NHSE_Reference.[dbo].[tbl_Ref_ODS_Commissioner_Hierarchies] rg
	ON apcs.Der_Postcode_CCG_Code = rg.Organisation_Code
left join NHSE_Reference.dbo.tbl_Ref_ODS_Provider_Hierarchies prov
	on apcs.Der_Provider_Code = prov.Organisation_Code
left join NHSE_Reference.dbo.tbl_Ref_NCB_NPoC_Map_2021 pss
	on der.NCBFinal_Spell_ServiceLine = pss.Service_Line
left join NHSE_Reference.dbo.tbl_Ref_ClinCode_OPCS opcs
	on left(substring(der_procedure_all, 3,4),4) = opcs.OPCS_L4_Code
left join  NHSE_Reference.[dbo].[tbl_Ref_ODS_ProviderSite] provsite
	on (case when apcs.Der_Provider_Site_Code = 'RHM00' THEN 'RHM01'   -- to fix default site code at University Hospital Southampton to show Southampton General site code
	         when apcs.Der_Provider_Site_Code = 'RK900' THEN 'RK950'   -- to fix default site code at University Hospitals Plymouth to show Derriford Hospital site code 
			 when apcs.Der_Provider_Site_Code = 'RAE00' THEN 'RAE01'   -- to fix default site code at Bradford Teaching Hospitals to show Bradford Royal Infirmary site code 
			 when apcs.Der_Provider_Site_Code = 'RAJ00' THEN 'RAJ12'   -- to fix default site code at Mid and South Essex to show Southampton General site code 
			 when apcs.Der_Provider_Site_Code = 'RYJ00' THEN 'RYJ03'   -- to fix default site code at Imperial College Healthcare to show Hammersmith Hospital site code 
			 WHEN apcs.Der_Provider_Site_Code = 'RXH00' THEN 'RXH01'   -- to fix default site code at University Hospital Southampton to show Southampton General site code 
			 else apcs.Der_Provider_Site_Code end) = provsite.Provider_Site_Code
LEFT JOIN #time time
		on replace(provsite.ODS_ProvSite_PostCode, ' ','') = time.to_postcode
		and replace(apcs.Der_Postcode_LSOA_2011_Code,' ','') = time.[from_postcode]
	

            """,
            language="sql",)