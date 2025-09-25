from pathlib import Path

from visualisation.VisualisationUtils import load_results


def latex_bold(str):
    return r"\textbf{" + f"{str}" + "}"

def GenerateLatexComparisonTable(results_paths:list[Path], save_table_path):
    
    table_columns_names = ["Metric Name"]
    dataset_names = []

    table_rows = {} #MetricName: val1,val2,val3,val4 ....

    results = {}

#       "kb_occurrence.json","class_occurrence.json",
    GRAMMAR = "Grammar Correctness"
    COHERENCE = "Coherence"
    CONSISTENCY = "Consistency"
    COMPLETENESS = "Completeness"
    CONTEXTDISP = "Context Dispersity"
    ANNOTDISP = "Annotation Dispersity"

    metric_file_names = {
        GRAMMAR:"grammar_correctness.json",
        COHERENCE:"entity_coherence.json",
        CONSISTENCY:"entity_consistency.json",
        COMPLETENESS:"entity_completeness.json",
        CONTEXTDISP:"dispersity_contexts.json",
        ANNOTDISP:"dispersity_annotations.json"
    }
    

    for result_path in results_paths:
        dataset_name = Path(result_path).stem
        table_columns_names.append(dataset_name)
        dataset_names.append(dataset_name)
        
        for metric in metric_file_names:
            ds_results_path = Path(result_path) / metric_file_names[metric]    
            
            if not ds_results_path.exists():
                continue
            results[metric] = results.get(metric,{})
            results[metric][dataset_name] = load_results(ds_results_path)
        
    grammar_res = results.get(GRAMMAR,None)
    if grammar_res is not None:
        table_rows[GRAMMAR] = {}

        temp_mean = []
        temp_sum = []
        for dataset_name in dataset_names:
            temp_mean.append(grammar_res[dataset_name]["errors_mean"])
            temp_sum.append(grammar_res[dataset_name]["errors_sum"])
        mean_min = min(temp_mean)
        sum_min = min(temp_sum)

        table_rows[GRAMMAR]["Errors mean"] = [f"{v:0.4f}" if v != mean_min else latex_bold(f"{v:0.4f}") for v in temp_mean]
        table_rows[GRAMMAR]["Errors sum"] =  [f"{v}" if v != sum_min else latex_bold(f"{v}") for v in temp_sum]

    coherence_res = results.get(COHERENCE,None)
    if coherence_res is not None:
        table_rows[COHERENCE] = {}

        temp_micro_NWD = []
        temp_macro_NWD = []
        for dataset_name in dataset_names:
            temp_micro_NWD.append(coherence_res[dataset_name]["micro_NWD"])
            temp_macro_NWD.append(coherence_res[dataset_name]["macro_NWD"])
        
        def min_format(val_list):
            return [f"{v:0.4f}" if v != min(val_list) else latex_bold(f"{v:0.4f}") for v in val_list]

        table_rows[COHERENCE]["Micro NWD"] = min_format(temp_micro_NWD)
        table_rows[COHERENCE]["Macro NWD"] = min_format(temp_macro_NWD)

    consistency_res = results.get(CONSISTENCY,None)
    if consistency_res is not None:
        table_rows[CONSISTENCY] = {}

        temp_micro_f1 = []
        temp_micro_f1_stdev = []

        temp_macro_f1 = []
        temp_macro_f1_stdev = []

        for dataset_name in dataset_names:
            temp_micro_f1.append(consistency_res[dataset_name]["micro_average_f1"])
            temp_micro_f1_stdev.append(consistency_res[dataset_name]["micro_f1_stdev"])
            temp_macro_f1.append(consistency_res[dataset_name]["macro_average_f1"])
            temp_macro_f1_stdev.append(consistency_res[dataset_name]["macro_f1_stdev"])

        def max_format(val_list):
            return [f"{v:0.4f}" if v != max(val_list) else latex_bold(f"{v:0.4f}") for v in val_list]
        def min_format(val_list):
            return [f"{v:0.4f}" if v != min(val_list) else latex_bold(f"{v:0.4f}") for v in val_list]
        
        table_rows[CONSISTENCY]["Micro average f1"] = max_format(temp_micro_f1)
        table_rows[CONSISTENCY]["Micro f1 stdev"] = min_format(temp_micro_f1_stdev)
        table_rows[CONSISTENCY]["Macro average f1"] = max_format(temp_macro_f1)
        table_rows[CONSISTENCY]["Macro f1 stdev"] = min_format(temp_macro_f1_stdev)

    completeness_res = results.get(COMPLETENESS,None)
    if completeness_res is not None:
        table_rows[COMPLETENESS] = {}

        temp_comp_fuz_100 = []
        temp_comp_fuz_80 = []
        temp_comp_fuz_60 = []
        temp_comp_str_100 = []
        temp_comp_str_80 = []
        temp_comp_str_60 = []
        for dataset_name in dataset_names:
            strict = completeness_res[dataset_name]["strict_completeness"]
            fuzzy = completeness_res[dataset_name]["fuzzy_completeness"]
            temp_comp_str_100.append(strict["1.0"])
            temp_comp_str_80.append(strict["0.8"])
            temp_comp_str_60.append(strict["0.6"])
            
            temp_comp_fuz_100.append(fuzzy["1.0"])
            temp_comp_fuz_80.append(fuzzy["0.8"])
            temp_comp_fuz_60.append(fuzzy["0.6"])

        def max_format(val_list):
            return [f"{v:0.4f}" if v != max(val_list) else latex_bold(f"{v:0.4f}") for v in val_list]
        
        table_rows[COMPLETENESS][r"Fuzzy T=100\%"] = max_format(temp_comp_fuz_100)
        table_rows[COMPLETENESS][r"Fuzzy T=80\%"] = max_format(temp_comp_fuz_80)
        table_rows[COMPLETENESS][r"Fuzzy T=60\%"] = max_format(temp_comp_fuz_60)
        table_rows[COMPLETENESS][r"Strict T=100\%"] = max_format(temp_comp_str_100)
        table_rows[COMPLETENESS][r"Strict T=80\%"] = max_format(temp_comp_str_80)
        table_rows[COMPLETENESS][r"Strict T=60\%"] = max_format(temp_comp_str_60)

    ctx_disp = results.get(CONTEXTDISP,None)
    if ctx_disp is not None:
        table_rows[CONTEXTDISP] = {}

        keyword_disp_euc = []
        keyword_disp_ang = []
        text_disp_euc = []
        text_disp_ang = []
        entityctx_disp_euc = []
        entityctx_disp_ang = []
        
        for dataset_name in dataset_names:
            keyword_disp_euc.append(ctx_disp[dataset_name]["context_keyword_dispersity"][0])
            keyword_disp_ang.append(ctx_disp[dataset_name]["context_keyword_dispersity_angular"][0])
        
            text_disp_euc.append(ctx_disp[dataset_name]["context_text_dispersity"][0])
            text_disp_ang.append(ctx_disp[dataset_name]["context_text_dispersity_angular"][0])
        
            entityctx_disp_euc.append(ctx_disp[dataset_name]["context_entities_dispersity"][0])
            entityctx_disp_ang.append(ctx_disp[dataset_name]["context_entities_dispersity_angular"][0])
        

        def max_format(val_list):
            return [f"{v:0.4f}" if v != max(val_list) else latex_bold(f"{v:0.4f}") for v in val_list]

        table_rows[CONTEXTDISP]["Keyword euclidean"] = max_format(keyword_disp_euc)
        table_rows[CONTEXTDISP]["Keyword angular"] = max_format(keyword_disp_ang)
        table_rows[CONTEXTDISP]["Text euclidean"] = max_format(text_disp_euc)
        table_rows[CONTEXTDISP]["Text angular"] = max_format(text_disp_ang)
        table_rows[CONTEXTDISP]["Entities' euclidean"] = max_format(entityctx_disp_euc)
        table_rows[CONTEXTDISP]["Entities' angular"] = max_format(entityctx_disp_ang)
        

    ctx_disp = results.get(ANNOTDISP,None)
    if ctx_disp is not None:
        table_rows[ANNOTDISP] = {}

        micro_eucl = []
        macro_eucl = []
        unique_eucl = []

        micro_ang = []
        macro_ang = []
        unique_ang = []
        
        for dataset_name in dataset_names:
            micro_eucl.append(ctx_disp[dataset_name]["micro_full_euclidean"][0])
            micro_ang.append(ctx_disp[dataset_name]["micro_full_angular"][0])
        
            macro_eucl.append(ctx_disp[dataset_name]["macro_dispersity_euclidean"][0])
            macro_ang.append(ctx_disp[dataset_name]["macro_dispersity_angular"][0])
        
            unique_eucl.append(ctx_disp[dataset_name]["micro_unique_euclidean"][0])
            unique_ang.append(ctx_disp[dataset_name]["micro_unique_angular"][0])
        

        def max_format(val_list):
            return [f"{v:0.4f}" if v != max(val_list) else latex_bold(f"{v:0.4f}") for v in val_list]

        table_rows[ANNOTDISP]["Micro euclidean"] = max_format(micro_eucl)
        table_rows[ANNOTDISP]["Micro angular"] = max_format(micro_ang)
        table_rows[ANNOTDISP]["Macro euclidean"] = max_format(macro_eucl)
        table_rows[ANNOTDISP]["Macro angular"] = max_format(macro_ang)
        table_rows[ANNOTDISP]["Unique euclidean"] = max_format(unique_eucl)
        table_rows[ANNOTDISP]["Unique angular"] = max_format(unique_ang)
        




    #Render Table
    columns_amount = len(dataset_names)
    table_result_str = r"\begin{tabular}{|c|c|"+ r"p{1.5cm}|"*columns_amount + "}" + "\n" + r"\hline" + "\n"
    headers = r"\multicolumn{2}{|c|}{\multirow{2}{*}{Metric Name}} & \multicolumn{" + str(columns_amount) + r"}{|c|}{Datasets} \\"+ "\n"  
    headers+= r"\cline{3-" + str(2+columns_amount) + "}" + "\n"
    headers+= r"\multicolumn{2}{|c|}{} " #cells under the metric name header
    
    for dataset_name in dataset_names:
        headers += f"& {dataset_name} "
    headers+= r"\\" + "\n" +r"\hline" + "\n"
    table_result_str = table_result_str + headers

    for category_name in table_rows:
        
        str_1 = r"\multirow{"+ str(len(table_rows[category_name])) +"}{*}{" + category_name + "}\n" 
        #str_2 = ""
        for metric_name in table_rows[category_name]:
            str_m = f"& {metric_name} " 
            for value in table_rows[category_name][metric_name]:
                str_m += f"& {value} "
            str_m += r"\\" +"\n"+ r"\cline{2-"+str(columns_amount+2)+"}\n"
            str_1 += str_m
        str_1 += r'\hline' + "\n"
        
        table_result_str += str_1
    table_result_str += r"\end{tabular}"

    print(table_result_str)
    # save_table_path = Path(save_table_path)
    # save_table_path.mkdir(exist_ok=True)