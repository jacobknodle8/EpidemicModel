ods rtf file='final_proj.rtf';

proc import datafile='Desktop/NDSU/STAT462/STAT462EpidemicSim/epidemic_data.csv'
	out=epidemic_data
	dbms=csv
	replace;
	getnames=yes;
run;

proc print data=epidemic_data;
run;

proc glm data=epidemic_data;
	class quarantine_prob mask_effectiveness;
	model max_infected = quarantine_prob mask_effectiveness quarantine_prob*mask_effectiveness;
	means quarantine_prob / tukey scheffe;
	lsmeans quarantine_prob mask_effectiveness*quarantine_prob / pdiff adjust=tukey;
	lsmeans quarantine_prob mask_effectiveness*quarantine_prob / pdiff adjust=scheffe;
	output out=residuals r=resid p=predicted;
run;

proc univariate data=residuals normal;
	var resid;
	histogram resid / normal;
	probplot resid / normal(mu=est sigma=est);
run;

proc sgplot data=residuals;
	scatter x=predicted y=resid;
	refline 0 / axis=y;
	xaxis label='Fitted Values';
	yaxis label='Residuals';
	title 'Residuals vs. Fitted Values';
run;

data residuals;
    set residuals;
    run_order = _N_;
run;

proc sgplot data=residuals;
    scatter x=run_order y=resid;
    refline 0 / axis=y;
    xaxis label="Run Order";
    yaxis label="Residuals";
    title "Residuals vs. Run Order";
run;

proc means data=epidemic_data mean std min max n;
    class quarantine_prob mask_effectiveness;
    var max_infected;
run;

proc sgplot data=epidemic_data;
    vbox max_infected / category=quarantine_prob;
    title "Boxplot of Peak Infections by Quarantine Level";
run;

proc sgplot data=epidemic_data;
    vbox max_infected / category=mask_effectiveness;
    title "Boxplot of Peak Infections by Masking Policy";
run;

data epidemic_data;
    set epidemic_data;
    group = cats("Q", quarantine_prob, "_M", mask_effectiveness);
run;

proc sgplot data=epidemic_data;
    vbox max_infected / category=group;
    title "Boxplot of Peak Infections by Treatment Combination";
run;

proc means data=epidemic_data noprint;
    class quarantine_prob mask_effectiveness;
    var max_infected;
    output out=means_data mean=mean_peak;
run;

proc sgplot data=means_data;
    series x=quarantine_prob y=mean_peak / group=mask_effectiveness markers;
    title "Interaction Plot: Quarantine × Masking";
    xaxis label="Quarantine Level";
    yaxis label="Mean Peak Infection";
run;

proc sgplot data=means_data;
    vbar quarantine_prob / response=mean_peak group=mask_effectiveness groupdisplay=cluster;
    title "Mean Peak Infection by Quarantine and Masking";
    yaxis label="Mean Peak Infection";
run;





quit;



