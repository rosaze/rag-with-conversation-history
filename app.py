import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os
from experiments.experiment_runner import ExperimentRunner
from utils.helpers import load_scenarios, save_results

# Page configuration
st.set_page_config(
    page_title="RAG Experiment Platform",
    page_icon="🔬",
    layout="wide"
)

def main():
    st.title("🔬 RAG Experiment Platform")
    st.markdown("Compare RAG approaches with conversation history integration")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    # API Key configuration
    openai_key = st.sidebar.text_input("OpenAI API Key", type="password", 
                                      value=os.getenv("OPENAI_API_KEY", ""))
    tavily_key = st.sidebar.text_input("Tavily API Key", type="password", 
                                      value=os.getenv("TAVILY_API_KEY", ""))
    
    if not openai_key:
        st.error("Please provide OpenAI API Key to continue")
        return
    
    # Load scenarios
    scenarios = load_scenarios()
    
    # Main navigation
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Run Experiment", "📋 Scenarios", "📈 Results", "⚙️ Settings"])
    
    with tab1:
        run_experiment_tab(scenarios, openai_key, tavily_key)
    
    with tab2:
        scenarios_tab(scenarios)
    
    with tab3:
        results_tab()
    
    with tab4:
        settings_tab()

def run_experiment_tab(scenarios, openai_key, tavily_key):
    st.header("Run RAG Experiment")
    
    # Experiment configuration
    col1, col2 = st.columns(2)
    
    with col1:
        selected_scenarios = st.multiselect(
            "Select Scenarios",
            options=[f"#{s['id']} - {s['domain']}" for s in scenarios],
            default=[f"#{scenarios[0]['id']} - {scenarios[0]['domain']}"] if scenarios else []
        )
        
        methods = st.multiselect(
            "Select Methods to Compare",
            options=["D1: LLM-only (no history)", "D2: LLM with history", 
                    "D3: RAG (current question)", "D4: RAG with history"],
            default=["D1: LLM-only (no history)", "D4: RAG with history"]
        )
    
    with col2:
        use_search = st.checkbox("Enable Real-time Search", value=True)
        search_engine = st.selectbox("Search Engine", ["Tavily", "Brave"], disabled=not use_search)
        
        max_results = st.slider("Max Search Results", 1, 10, 5)
        temperature = st.slider("LLM Temperature", 0.0, 1.0, 0.7)
    
    if st.button("🚀 Run Experiment", type="primary"):
        if not selected_scenarios or not methods:
            st.error("Please select at least one scenario and one method")
            return
        
        # Extract scenario IDs
        scenario_ids = [int(s.split('#')[1].split(' ')[0]) for s in selected_scenarios]
        selected_scenario_data = [s for s in scenarios if s['id'] in scenario_ids]
        
        # Initialize experiment runner
        runner = ExperimentRunner(
            openai_key=openai_key,
            tavily_key=tavily_key if use_search else None,
            search_engine=search_engine if use_search else None,
            temperature=temperature,
            max_results=max_results
        )
        
        # Run experiments
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()
        
        all_results = []
        total_experiments = len(selected_scenario_data) * len(methods)
        current_experiment = 0
        
        for scenario in selected_scenario_data:
            st.subheader(f"Scenario #{scenario['id']}: {scenario['domain']}")
            
            # Display scenario context
            with st.expander("View Scenario Details"):
                st.write("**Conversation History:**")
                for i, msg in enumerate(scenario['conversation_history'], 1):
                    st.write(f"{i}. {msg}")
                st.write(f"**Current Question:** {scenario['current_question']}")
                st.write(f"**Expected Focus:** {', '.join(scenario['expected_focus'])}")
                st.write(f"**Context Dependency:** {scenario['context_dependency']}")
            
            scenario_results = {}
            
            for method in methods:
                current_experiment += 1
                progress_bar.progress(current_experiment / total_experiments)
                status_text.text(f"Running {method} on {scenario['domain']} scenario...")
                
                try:
                    if method.startswith("D1"):
                        result = runner.run_d1(scenario['current_question'])
                    elif method.startswith("D2"):
                        result = runner.run_d2(scenario['conversation_history'], scenario['current_question'])
                    elif method.startswith("D3"):
                        result = runner.run_d3(scenario['current_question'])
                    elif method.startswith("D4"):
                        result = runner.run_d4(scenario['conversation_history'], scenario['current_question'])
                    
                    scenario_results[method] = result
                    
                    # Display result
                    with st.expander(f"📝 {method} Response"):
                        st.write(result['response'])
                        if 'search_results' in result:
                            st.write("**Search Results Used:**")
                            for i, doc in enumerate(result['search_results'][:3], 1):
                                st.write(f"{i}. {doc.get('title', 'No title')}")
                
                except Exception as e:
                    st.error(f"Error running {method}: {str(e)}")
                    scenario_results[method] = {"response": f"Error: {str(e)}", "error": True}
            
            # Save results
            result_entry = {
                "timestamp": datetime.now().isoformat(),
                "scenario_id": scenario['id'],
                "domain": scenario['domain'],
                "results": scenario_results
            }
            all_results.append(result_entry)
        
        # Save all results
        save_results(all_results)
        
        progress_bar.progress(1.0)
        status_text.text("✅ Experiment completed!")
        
        st.success(f"Experiment completed! Results saved for {len(selected_scenario_data)} scenarios.")

def scenarios_tab(scenarios):
    st.header("📋 Experiment Scenarios")
    
    if not scenarios:
        st.warning("No scenarios loaded. Please check the scenarios.json file.")
        return
    
    # Display scenarios in a table
    scenario_df = pd.DataFrame([
        {
            "ID": s['id'],
            "Domain": s['domain'],
            "Difficulty": s['difficulty'],
            "Context Dependency": s['context_dependency'],
            "History Length": len(s['conversation_history']),
            "Question": s['current_question'][:100] + "..." if len(s['current_question']) > 100 else s['current_question']
        }
        for s in scenarios
    ])
    
    st.dataframe(scenario_df, use_container_width=True)
    
    # Detailed view
    selected_id = st.selectbox("View Scenario Details", 
                              options=[s['id'] for s in scenarios],
                              format_func=lambda x: f"#{x} - {next(s['domain'] for s in scenarios if s['id'] == x)}")
    
    if selected_id:
        scenario = next(s for s in scenarios if s['id'] == selected_id)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Scenario Information")
            st.write(f"**Domain:** {scenario['domain']}")
            st.write(f"**Difficulty:** {scenario['difficulty']}")
            st.write(f"**Context Dependency:** {scenario['context_dependency']}")
            
            st.subheader("Expected Focus Areas")
            for focus in scenario['expected_focus']:
                st.write(f"• {focus}")
        
        with col2:
            st.subheader("Conversation History")
            for i, msg in enumerate(scenario['conversation_history'], 1):
                st.write(f"**Turn {i}:** {msg}")
            
            st.subheader("Current Question")
            st.write(scenario['current_question'])

def results_tab():
    st.header("📈 Experiment Results")
    
    # Load results
    results_file = "data/results.json"
    if not os.path.exists(results_file):
        st.info("No experiment results found. Run an experiment first.")
        return
    
    with open(results_file, 'r', encoding='utf-8') as f:
        all_results = json.load(f)
    
    if not all_results:
        st.info("No experiment results found.")
        return
    
    # Display recent experiments
    st.subheader("Recent Experiments")
    
    # Group by timestamp for better organization
    experiments_df = []
    for result in all_results:
        for method, method_result in result['results'].items():
            experiments_df.append({
                "Timestamp": result['timestamp'][:19],  # Remove microseconds
                "Domain": result['domain'],
                "Scenario ID": result['scenario_id'],
                "Method": method,
                "Has Error": method_result.get('error', False),
                "Response Length": len(method_result.get('response', ''))
            })
    
    df = pd.DataFrame(experiments_df)
    st.dataframe(df, use_container_width=True)
    
    # Detailed result view
    if st.button("🔍 Analyze Results"):
        st.subheader("Method Comparison")
        
        # Count by method
        method_counts = df['Method'].value_counts()
        st.bar_chart(method_counts)
        
        # Average response length by method
        avg_length = df.groupby('Method')['Response Length'].mean()
        st.subheader("Average Response Length by Method")
        st.bar_chart(avg_length)
        
        # Error rate by method
        error_rate = df.groupby('Method')['Has Error'].mean() * 100
        st.subheader("Error Rate by Method (%)")
        st.bar_chart(error_rate)
    
    # Export results
    if st.button("📥 Export Results"):
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"rag_experiment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def settings_tab():
    st.header("⚙️ Settings")
    
    st.subheader("API Configuration")
    st.info("API keys are configured in the sidebar for security.")
    
    st.subheader("Experiment Parameters")
    st.write("Default parameters can be adjusted in the Run Experiment tab.")
    
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Results"):
            if os.path.exists("data/results.json"):
                os.remove("data/results.json")
                st.success("Results cleared!")
                st.rerun()
    
    with col2:
        if st.button("📊 Reload Scenarios"):
            st.success("Scenarios will be reloaded on next page refresh!")
            st.rerun()

if __name__ == "__main__":
    main()
