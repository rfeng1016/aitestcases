import Agently
import json
from ENV import deep_seek_url, deep_seek_api_key, deep_seek_default_model
from md_to_txt import text_pieces

# 将模型请求配置设置到agent工厂，确保后续由该工厂创建的所有agent对象都能继承这些配置
agent_factory = (
    Agently.AgentFactory()
    .set_settings("current_model", "OAIClient")
    .set_settings("model.OAIClient.url", deep_seek_url)
    .set_settings("model.OAIClient.auth", {"api_key": deep_seek_api_key})
    .set_settings("model.OAIClient.options", {"model": deep_seek_default_model})
)

"""
工作流程：
需求文档（requirement_document）--> 
归纳业务模块摘要（requirement_summary）-->  
对摘要进行业务细化（detailed_summary）--> 
根据摘要和细化业务画出流程图（flow_chart）--> 
按流程图编辑测试用例（test_case）

First Question：
1.角色设定：你是专业的需求分析师（Demand analyst），熟悉业务需求逻辑分析
2.输入信息：分析需求文档中的业务模块，归纳整理出模块摘要
3.输出信息：基于输入信息，对需求文档进行摘要生成
4.人类判断是否满意

Second Question：
1.角色设定：你是专业的需求分析师（Demand analyst），熟悉业务需求逻辑分析
2.输入信息：根据需求文档对生成的摘要进行细化
3.输出信息：生成详细内容
4.反思agent（产品经理（Product manager））发起反思任务

Third Question：
1.角色设定：
2.输入信息：针对摘要和细化内容，梳理出流程图，并使用mermaid代码输出
3.输出信息：生成mermaid代码
4.反思agent（项目经理（Project manager））发起反思任务

Fourth Question：
1.角色设定：资深功能测试工程师（Test engineer）
2.输入信息：按流程图编辑测试用例
3.输出信息：生成MD格式测试用例
4.人类判断是否满意
"""

# 创建一个工作流实例
workflow = Agently.Workflow()

# 主要工作：将需求文档中的业务模块归纳整理为摘要
@workflow.chunk()
def first_question(inputs, storage):
    # 需求文档
    requirement_document = storage.get("requirement_document")

    # 创建需求分析agent来执行任务
    demand_agent = agent_factory.create_agent()

    # 设置需求分析agent的角色信息
    demand_agent.set_agent_prompt(
        "role",
        f"你是专业的需求分析工程师，擅长{requirement_document}的业务逻辑分析。"
    )

    # 发起归纳需求模块摘要任务请求
    requirement_summary = (demand_agent.input(f"""分析{requirement_document}包含的业务模块，将业务模块进行归纳整理为摘要。 \
        请根据{requirement_document}内容，不要提供任何文档之外的摘要内容。 \
        {requirement_document}: """).start())
    
    # 保存业务摘要结果和需求分析agent
    storage.set("requirement_summary", requirement_summary)
    storage.set("demand_agent", demand_agent)

    # 返回摘要和结果
    return {
        "stage": "First Question：归纳整理需求中的业务模块为摘要",
        "result": requirement_summary
    }

# 主要工作：将上面的摘要进行业务模块细化
@workflow.chunk()
def second_question(inputs, storage):
    # 获取需求摘要内容
    requirement_summary = storage.get("requirement_summary")

    # 使用之前保存的需求分析agent
    demand_agent = storage.get("demand_agent")

    # 发起各个模块的摘要进行业务细化任务请求
    detailed_summary = (demand_agent.input(f"""分析{requirement_summary}的业务模块摘要，对各个模块里的页面进行细化。 \
        请根据{requirement_summary}内容，不要提供任何文档之外的细化内容。 \
        {requirement_summary}: """).start())

    # 保存细化内容结果和需求agent
    storage.set("detailed_summary", detailed_summary)
    # storage.set("demand_agent", demand_agent)

    # 返回细化摘要和结果
    return {
        "stage": "Second Question：各个模块下的页面进行业务细化",
        "result": detailed_summary
    }

# 针对摘要和内容，梳理出流程图，并使用mermaid代码输出，在mermaid工具中将这个图绘制出来。
@workflow.chunk()
def third_question(inputs, storage):
    # 获取需求摘要内容
    requirement_summary = storage.get("requirement_summary")

    # 获取细化摘要内容
    detailed_summary = storage.get("requirement_summary")

    # 使用之前保存的需求分析agent
    demand_agent = storage.get("demand_agent")

    # 发起流程图任务请求
    flow_chart = (demand_agent.input(f"""针对{requirement_summary}和{detailed_summary}梳理流程，找出各个页面之间的流转关系，并使用mermaid代码输出。 \
            请根据{requirement_summary}和{detailed_summary}内容，不要提供任何文档之外的细化内容。 \
            {detailed_summary}: """).start())

    # 保存流程图结果和需求agent
    storage.set("demand_agent", demand_agent)
    storage.set("flow_chart", flow_chart)

    # 返回阶段和结果
    return {
        "stage": "Third Question：输出流程图的mermaid代码",
        "result": flow_chart
    }

# 设置需求分析agent的角色信息（改为：反思agent（产品经理（Product manager））发起反思任务）
# demand_agent.set_agent_prompt(
#     "role",
#     f"你是专业的需求分析师，擅长{requirement_summary}的业务模块摘要细化逻辑。"
# )

# 按流程图编辑测试用例,覆盖所有的路径分支
@workflow.chunk()
def fourth_question(inputs, storage):
    # 获取需求摘要内容
    requirement_summary = storage.get("requirement_summary")

    # 获取细化摘要内容
    detailed_summary = storage.get("requirement_summary")

    # 获取流程图内容
    flow_chart = storage.get("flow_chart")

    # 创建测试agent来执行任务
    test_agent = agent_factory.create_agent()

    # 设置测试agent的角色信息
    test_agent.set_agent_prompt(
        "role",
        f"你是专业的软件测试工程师，擅长对{flow_chart}进行测试用例编写。"
    )

    # 发起流程图任务请求
    test_case = (test_agent.input(f"""按照{flow_chart}编辑测试用例,覆盖所有的路径分支。并使用markdown代码输出。 \
              请根据{requirement_summary}、{detailed_summary}和{flow_chart}内容，不要提供任何文档之外的测试用例。 \
              {detailed_summary}: """).start())

    # 保存流程图结果和需求agent
    storage.set("test_agent", test_agent)
    storage.set("test_case", test_case)

    # 返回阶段和结果
    return {
        "stage": "Fourth Question：归纳需求中的业务模块为摘要",
        "result": test_case
    }


# 定义工作流运行关系
(
    workflow
    .connect_to("first_question")
    .connect_to("second_question")
    .connect_to("third_question")
    .connect_to("fourth_question")
    .connect_to("END")  # 连接到系统内置的end块
)

# 添加过程输出优化
@workflow.chunk_class()
def output_stage_result(inputs, storage):
    # 打印每个阶段的结果
    print(f"[{inputs['default']['stage']}]:\n", inputs["default"]["result"])
    return

# 连接输出节点到各工作块
(
    workflow.chunks["first_question"]
    .connect_to("@output_stage_result")
    .connect_to("second_question.wait")
)
(
    workflow.chunks["second_question"]
    .connect_to("@output_stage_result")
    .connect_to("third_question.wait")
)
(
    workflow.chunks["third_question"]
    .connect_to("@output_stage_result")
    .connect_to("fourth_question.wait")
)
(
    workflow.chunks["fourth_question"]
    .connect_to("@output_stage_result")
)

# 启动工作流并传入初始化存储数据
result = workflow.start(storage={"requirement_document": text_pieces[0]})

# 打印最终结果，使用json格式化输出
print(json.dumps(result, indent=4, ensure_ascii=False))



