# -*- coding: utf-8 -*-
import re
import streamlit as st

from Judge_Agent import Judge_Agent
from Plantiff_Agent import Plantiff_Agent
from Defendant_Agent import Defendant_Agent


with open('./laws.txt','r', encoding='utf-8') as file:
    laws = file.read()

plantiff_evidences = '''
1、被告工商登记信息	；证明目的：伯乐公司是一家有偿经营相关人力资源信息的专业数据服务提供商，为不正当竞争纠纷适格主体。
2、俊杰平台《隐私政策》、俊杰平台《用户协议》；证明目的：伯乐公司无权擅自搜集、分析、加工和使用俊杰公司网上的信息，侵犯了该平台上用户的信息权益。
3、俊杰公司2020年11月2日向伯乐公司发出的《律师函》、伯乐公司11月30日回函；证明目的：俊杰公司要求伯乐公司停止不正当竞争行为，伯乐公司拒绝。
'''

defendant_evidences = '''
1、俊杰平台《隐私政策》、俊杰平台《用户协议》；证明目的：用户档案信息为公开信息，伯乐公司仅利用公开的信息进行合理的数据分析。
2、伯乐公司《隐私政策》；证明目的伯乐公司对数据安全持审慎态度，用户 有权要求伯乐公司随时删除其公开信息。
3、俊杰公司于2018年上半年起曾数次派员参加伯乐公司会议的《会议纪要》；证明目的：俊杰公司一直知晓并默认伯乐公司的行为
'''

with st.sidebar:
    api_key_input1 = st.text_input(
        "OpenAI API Key1",
        type="password",
        placeholder="Paste your OpenAI API key here (sk-...)",
        help="You can get your API key from https://platform.openai.com/account/api-keys.",  # noqa: E501
    )
    api_key_input2 = st.text_input(
        "OpenAI API Key2",
        type="password",
        placeholder="Paste your OpenAI API key here (sk-...)",
        help="You can get your API key from https://platform.openai.com/account/api-keys.",  # noqa: E501
    )
    api_key_input3 = st.text_input(
        "OpenAI API Key3",
        type="password",
        placeholder="Paste your OpenAI API key here (sk-...)",
        help="You can get your API key from https://platform.openai.com/account/api-keys.",  # noqa: E501
    )

    case = st.text_area('案件事实', '')
    # laws = st.text_area('相关法条', '')
    plantiff = st.text_input('原告', '')
    # plantiff_evidences = st.text_area('原告证据', '')
    defendant = st.text_input('被告', '')
    # defendant_evidences = st.text_area('被告证据', '')
    start = st.button("Let's go!", type="primary")


st.title('MootCourt :male-judge:')
# class Court(): // court类相当于主持人的作用，控制整个流程？
class Court:
    def __init__(self,
                 model_name: str = 'gpt-3.5-turbo',
                 temperature: float = 0,
                 save_file_dir: str = None,
                 openai_api_key: str = None,
                 prompts_path: str = None,
                 sleep_time: float = 0

                 ) -> None:
        self.judge_agent = Judge_Agent(model_name="gpt-3.5-turbo-16k", name="法官", temperature=0.1,
                                       openai_api_key=api_key_input1)
        self.plantiff_agent = Plantiff_Agent(model_name="gpt-3.5-turbo-16k", name="原告方", temperature=0.5,
                                             openai_api_key=api_key_input2)
        self.defendant_agent = Defendant_Agent(model_name="gpt-3.5-turbo-16k", name="被告方", temperature=0.5,
                                               openai_api_key=api_key_input3)
        self.disputed_points = ''
        self.investigate_process = ''
        self.evidence_process = ''
        self.debate_process = ''
        self.final_statement_process = ''

    def init_prompt(self,case,plantiff,defendant,laws):
        self.judge_agent.set_meta_prompt(
            "现在是一场庭审现场，有审判长，原告方，被告方三种角色，你是一名审判长，你的语气要尽可能简洁和威严，不要使用敬语，法庭共分为法庭调查（原告宣读起诉书、被告宣读答辩状、审判长总结争议焦点）—举证质证（双方提交证据并可对证据可信性质疑）—法庭辩论（双方发表辩论意见）-最后陈述（双方对辩论观点进行总结，审判长宣读本案判决）四个阶段，采用问询制度，你可以向他们行使审问权力，每轮审问仅可面向一人（原告或者被告），如果是询问要指出询问对象并在末尾标注标签，0表示提问原告，1表示提问被告，如，'审判长：由原告回答xxx（label：0）'//现有案件如下：{}//现在开庭，请你确认双方信息（原告：{}，被告：{}，开始主持：".format(case,plantiff,defendant))

        self.plantiff_agent.set_meta_prompt(
            "现在是一场庭审现场，有审判长，原告方，被告方三种角色，你是原告方的代理律师，你的目标是在法庭上依据现实情况和已有证据努力维护原告的利益，在遵循法律的条件下赢下这场官司。法庭采取问询制度，每轮审问审判长仅面向一人（原告或被告）要求做出回答，法官未要求你陈述时不得发言，扰乱秩序。回答要简洁有理，首先表明身份，如：原告方：xx。//现有案件如下：{}//现在进入开庭，你是原告：{}的代理律师，可参考的法律条文有{}，请等待审判长提问，确认你的信息，并分点提出你方的诉求:".format(case,plantiff,laws))

        self.defendant_agent.set_meta_prompt(
            "现在是一场庭审现场，有审判长，原告方，被告方三种角色，你是被告方的代理律师，你的目标是在法庭上依据现实情况和已有证据努力维护被告的利益，在遵循法律的条件下赢下这场官司。法庭采取问询制度，每轮审问审判长仅面向一人（原告或被告）要求做出回答，法官未要求你陈述时不得发言，扰乱秩序。回答要简洁有理，首先表明身份，如：被告方：xx。//现有案件如下：{}//现在进入开庭，你是被告：{}的代理律师，可参考的法律条文有{},请等待审判长提问，确认你的信息，并分点提出你方的诉求:".format(case,defendant,laws))

    def investigate(self):
        st.subheader('法庭调查', divider='rainbow')
        judge_prompt = '请审判长宣布进行法庭调查，可以选择是否对调查程序进行详细的说明。请原告方宣读起诉状起诉书。'
        self.judge_agent.add_event(judge_prompt)
        response = self.judge_agent.ask()
        with st.chat_message("assistant"):
            st.write(response)
        print("response1",response)
        self.judge_agent.add_memory(response)
        self.plantiff_agent.add_event(response)
        self.defendant_agent.add_event(response)

        #原告宣读起诉书
        plantiff_prompt = '''请你宣读起诉状，起诉状的内容包括根据案件证据，归纳出的具体明确的诉讼请求以及起诉所依据的事实与理由。可以先进行案件事实的陈述、再分点说明起诉理由，最后进行总结，向法院重申诉讼请求。'''
        self.plantiff_agent.add_event(plantiff_prompt)
        response = self.plantiff_agent.ask()
        self.plantiff_agent.del_memory()
        print('response2',response)
        with st.chat_message("user"):
            st.write(response)
        self.plantiff_agent.add_memory(response)
        self.judge_agent.add_event(response)
        self.defendant_agent.add_event(response)


        #被告宣读答辩状
        self.judge_agent.add_event("请让被告方宣读答辩状。")
        response = self.judge_agent.ask()
        print("response1", response)
        with st.chat_message("assistant"):
            st.write(response)
        self.judge_agent.add_memory(response)
        self.plantiff_agent.add_event(response)
        self.defendant_agent.add_event(response)
        defendant_prompt = '''请你宣读答辩状，内容包括根据案件相关事实，归纳出的具体明确的答辩事实与理由。可以分点说明答辩理由。'''
        self.defendant_agent.add_event(defendant_prompt)
        response = self.defendant_agent.ask()
        self.defendant_agent.del_memory()
        print('response3', response)
        with st.chat_message("user"):
            st.write(response)
        self.defendant_agent.add_memory(response)
        self.judge_agent.add_event(response)
        self.plantiff_agent.add_event(response)

        #审判长总结争议焦点
        judge_prompt = '''请根据原告方的陈述和被告方的答辩，总结争议焦点，可以从适用法律法规、事实、程序 等方面考虑。你的总结措辞应该尽量简洁严谨,争议焦点不能超过三点。 
        可参考示例如下：根据原告方的起诉状和被告方的答辩状，合议庭认为本案的争议焦点有三点：
1、鸿宣化工有限公司与第三方公司浦江县聚鑫化工有限公司、兰溪旭日化工有限公司之间是否形成交易关系？
2、被告浦江县公安局作出的浦公（禁毒）行罚决字[2019]51476号行政处罚决定书适用法律是否正确？
3、被告浦江县公安局作出行政处罚程序是否存在瑕疵？
'''
        self.judge_agent.add_event(judge_prompt)
        response = self.judge_agent.ask()
        self.disputed_points = response
        self.judge_agent.del_memory()
        print("response1", response)
        with st.chat_message("assistant"):
            st.write(response)
        self.judge_agent.add_memory(response)
        self.plantiff_agent.add_event(response)
        self.defendant_agent.add_event(response)
        self.disputed_points =response


    def evidence(self,plantiff_evidences,defendant_evidences):
        st.subheader('举证质证', divider='rainbow')
        #原告方举证、被告方质证
        judge_prompt = '请审判长宣布进入举证质证环节，首先由原告进行举证。'
        self.judge_agent.add_event(judge_prompt)
        response = self.judge_agent.ask()
        print("response1", response)
        with st.chat_message("assistant"):
            st.write(response)
        self.judge_agent.add_memory(response)
        self.plantiff_agent.add_event(response)
        self.defendant_agent.add_event(response)

        # 原告举证
        plantiff_prompt = f'''现有证据如下：{plantiff_evidences}，请你进行举证，依据证明目的将证据分组阐述，每组中的各条证据用于佐证证明目的，并逐条说明。形式如：“证据一、证据内容；证明目的”；可参考示例如下：证据一、南京市江宁区工商行政管理局公司准予变更登记通知书一份、南京业华铸造工艺有限公司股东会决议一份,股东名册一份、营业执照副本一份；证明2015年的4月23日，业华公司将注册资本从51万元增加至800万元，增加的注册资本749万元中，孙巧安于2025年4月20日以货币形式出资279万元,朱治家于2025年4月20日以货币方式出资出资470万元，增加的注册资本中，孙巧安出资额是300万元，占注册资本的37.5%,朱治家出资额是500万元，占注册资本的62.5%。'''
        self.plantiff_agent.add_event(plantiff_prompt)
        response = self.plantiff_agent.ask()
        print('response2', response)
        with st.chat_message("user"):
            st.write(response)
        self.plantiff_agent.add_memory(response)
        self.judge_agent.add_event(response)
        self.defendant_agent.add_event(response)
        #被告质证
        self.judge_agent.add_event("请让被告对原告的举证进行质证。")
        response = self.judge_agent.ask()
        print("response1", response)
        with st.chat_message("assistant"):
            st.write(response)
        self.judge_agent.add_memory(response)
        self.plantiff_agent.add_event(response)
        self.defendant_agent.add_event(response)
        defendant_prompt = '''请你分条对原告的证据进行质证，从真实性、关联性、证明目的等方面展开。如果对其中某条证据的真实性、关联性、证明目的无异议，则对此条证据无需进行质证；如果对其中某条证据的真实性、关联性、证明目的有异议，则需具体说明异议理由，即为什么认为该证据缺乏真实性或关联性。可参考示例如下：对原告提供的这一整套的工商登记的真实性没有异议,但是被告孙巧安想说明的是，该组证据所有关于生巧案的签名并非是其本人所写，所以对此住此组证据的合法性提出质疑。'''
        self.defendant_agent.add_event(defendant_prompt)
        response = self.defendant_agent.ask()
        print('response3', response)
        with st.chat_message("user"):
            st.write(response)
        self.defendant_agent.add_memory(response)
        self.judge_agent.add_event(response)
        self.plantiff_agent.add_event(response)

        #被告方举证、原告方质证
        # 被告举证
        judge_prompt = '请审判长提示被告进行举证。'
        self.judge_agent.add_event(judge_prompt)
        response = self.judge_agent.ask()
        print("response1", response)
        with st.chat_message("assistant"):
            st.write(response)
        self.judge_agent.add_memory(response)
        self.plantiff_agent.add_event(response)
        self.defendant_agent.add_event(response)

        defendant_prompt = f'''现有证据如下：{defendant_evidences}，请你进行举证，依据证明目的将证据分组阐述，每组中的各条证据用于佐证证明目的，并逐条说明。形式如：“证据一、证据内容；证明目的”；可参考示例如下：证据一、南京市江宁区工商行政管理局公司准予变更登记通知书一份、南京业华铸造工艺有限公司股东会决议一份,股东名册一份、营业执照副本一份；证明2015年的4月23日，业华公司将注册资本从51万元增加至800万元，增加的注册资本749万元中，孙巧安于2025年4月20日以货币形式出资279万元,朱治家于2025年4月20日以货币方式出资出资470万元，增加的注册资本中，孙巧安出资额是300万元，占注册资本的37.5%,朱治家出资额是500万元，占注册资本的62.5%。'''
        self.defendant_agent.add_event(defendant_prompt)
        response = self.defendant_agent.ask()
        print('response3', response)
        with st.chat_message("user"):
            st.write(response)
        self.defendant_agent.add_memory(response)
        self.judge_agent.add_event(response)
        self.plantiff_agent.add_event(response)
        # 原告质证
        self.judge_agent.add_event("请让原告对被告的举证进行质证。")
        response = self.judge_agent.ask()
        print("response1", response)
        with st.chat_message("assistant"):
            st.write(response)
        self.judge_agent.add_memory(response)
        self.plantiff_agent.add_event(response)
        self.defendant_agent.add_event(response)
        plantiff_prompt = '''请你分条对被告的证据进行质证，从真实性、关联性、证明目的等方面展开。如果对其中某条证据的真实性、关联性、证明目的无异议，则对此条证据无需进行质证；如果对其中某条证据的真实性、关联性、证明目的有异议，需具体说明异议的理由，即为什么认为该证据缺乏真实性或关联性。可参考示例如下：对原告提供的这一整套的工商登记的真实性没有异议,但是被告孙巧安想说明的是，该组证据所有关于生巧案的签名并非是其本人所写，所以对此住此组证据的合法性提出质疑。'''
        self.plantiff_agent.add_event(plantiff_prompt)
        response = self.plantiff_agent.ask()
        print('response2', response)
        with st.chat_message("user"):
            st.write(response)
        self.plantiff_agent.add_memory(response)
        self.judge_agent.add_event(response)
        self.defendant_agent.add_event(response)


    def debate(self):
        st.subheader('法庭辩论', divider='rainbow')
        judge_prompt = "下面进入法庭辩论环节，辩论环节针对争议焦点展开，你需要对每个争议焦点主持一轮辩论，整个流程为：原告发表辩论意见-被告被告发表辩论意见......，即原被告交替发表辩论意见，直至双方均无新的意见补充时结束本环节。每轮辩论提问时，你需要指出询问对象并在文本末尾标注label，0表示提问原告，1表示提问被告，如，'审判长：由原告回答xxx（label：0）。首先请你由原告发表辩论意见（label：0）。"
        plantiff_prompt = '''下面进入法庭辩论环节，当审判长提问你时，你需要发表辩论意见，辩论意见可以结合被告答辩状、被告质证、被告举证的内容，从法律适用、事实认定、程序合法性等方面考虑 。
        '''
        defendant_prompt = '''下面进入法庭辩论环节，当审判长提问你时，你需要发表辩论意见，辩论意见可以结合被告答辩状、被告质证、被告举证的内容，从法律适用、事实认定、程序合法性等方面考虑 。
       '''
        self.plantiff_agent.add_event(plantiff_prompt)
        self.defendant_agent.add_event(defendant_prompt)

        #轮数不准确
        numbers = re.findall(r'\d+', self.disputed_points)
        rounds = max(map(int,numbers))

        self.judge_agent.add_event(judge_prompt)
        for j in range(rounds):
            i = 1
            num = j + 1
            self.judge_agent.add_event(f"下面请你主持关于第{num}点争议焦点的辩论")
            while (1):
                # self.judge_agent.add_event(judge_prompt)
                response = self.judge_agent.ask()
                print("response1", response)
                with st.chat_message("assistant"):
                    st.write(response)
                self.judge_agent.add_memory(response)
                self.plantiff_agent.add_event(response)
                self.defendant_agent.add_event(response)
                if "0" in response:
                    self.plantiff_agent.add_event(f"请围绕第{num}点争议焦点发表辩论意见")
                    response = self.plantiff_agent.ask()
                    print("response2", response)
                    with st.chat_message("user"):
                        st.write(response)
                    self.plantiff_agent.add_memory(response)
                    self.judge_agent.add_event(response)
                    self.defendant_agent.add_event(response)
                else:
                    self.plantiff_agent.add_event(f"请围绕第{num}点争议焦点发表辩论意见")
                    response = self.defendant_agent.ask()
                    print("response3", response)
                    with st.chat_message("user"):
                        st.write(response)
                    self.defendant_agent.add_memory(response)
                    self.judge_agent.add_event(response)
                    self.plantiff_agent.add_event(response)
                i = i + 1
                if i == 3:
                    break
        # print("judge_agent.memory_lst",self.judge_agent.memory_lst)
        # print("plantiff_agent.memory_lst",self.plantiff_agent.memory_lst)

    def final_statement(self):
        st.subheader('最后陈述', divider='rainbow')
        judge_prompt = "双方无新的辩论意见或发表与案件争议焦点无关的意见后，开始进入最后陈述环节，首先请你由原告进行最后陈述。"
        self.judge_agent.add_event(judge_prompt)
        response = self.judge_agent.ask()
        print("response1", response)
        with st.chat_message("assistant"):
            st.write(response)
        self.judge_agent.add_memory(response)
        self.plantiff_agent.add_event(response)
        self.defendant_agent.add_event(response)

        #原告最后陈述
        plantiff_prompt = "请你发表最后陈述，最后陈述应结合法庭调查、法庭辩论中本方的观点，同时对被告的观点进行反驳。可参考示例如：请求法院依法支持原告的全部诉讼请求。"
        self.plantiff_agent.add_event(plantiff_prompt)
        response = self.plantiff_agent.ask()
        self.plantiff_agent.del_memory()
        print('response2', response)
        with st.chat_message("user"):
            st.write(response)
        self.plantiff_agent.add_memory(response)
        self.judge_agent.add_event(response)
        self.defendant_agent.add_event(response)

        # 被告最后陈述
        self.judge_agent.add_event("请让被告发表最后陈述。")
        response = self.judge_agent.ask()
        print("response1", response)
        with st.chat_message("assistant"):
            st.write(response)
        self.judge_agent.add_memory(response)
        self.plantiff_agent.add_event(response)
        self.defendant_agent.add_event(response)
        defendant_prompt = '''请你发表最后陈述，最后陈述应结合法庭调查、法庭辩论中本方的观点，同时对原告的观点进行反驳。可参考示例如：请求法院依法驳回原告的全部诉讼请求。'''
        self.defendant_agent.add_event(defendant_prompt)
        response = self.defendant_agent.ask()
        self.defendant_agent.del_memory()
        print('response3', response)
        with st.chat_message("user"):
            st.write(response)
        self.defendant_agent.add_memory(response)
        self.judge_agent.add_event(response)
        self.plantiff_agent.add_event(response)

        judge_prompt = "根据原被告双方在法庭调查、法庭辩论阶段陈述的观点，请你分别对原告起诉状中的内容进行审查，判断是否支持，作出支持原告诉讼请求或者驳回原告诉讼请求的判决。"
        self.judge_agent.add_event(judge_prompt)
        response = self.judge_agent.ask()
        print("response1", response)
        with st.chat_message("assistant"):
            st.write(response)


if start:
    court = Court()
    court.init_prompt(case,plantiff,defendant,laws)
    court.investigate()
    court.evidence(plantiff_evidences,defendant_evidences)
    court.debate()
    court.final_statement()

