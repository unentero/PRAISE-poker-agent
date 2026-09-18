from renderers import NullRenderer
from statebuffer import StateBuffer
from pokerRenderer import ConsoleRenderer
from pokerTable import PokerTable
from pokerAgents import PokerAgent
import threading

agent_finished_flag = False
event_render_ready = threading.Event()

def agent_thread(agent):
    global agent_finished_flag
    for _ in range(10):
        event_render_ready.wait(timeout=0.1)
        agent.behave()
        event_render_ready.clear()
    agent_finished_flag = True

def render_thread(renderer):
    while not agent_finished_flag:
        renderer.render()
        event_render_ready.set()

if __name__ == '__main__':
    env = PokerTable()
    agent1 = PokerAgent(env)
    agent2 = PokerAgent(env)
    env.prepare_stage_0(1000)  #test

    #agent3 = PokerAgent(env)
    #agent4 = PokerAgent(env)
    renderer = ConsoleRenderer()
    statebuffer = StateBuffer(agent1.id)
    
    env.add_statebuffer(agent1.id, statebuffer)
    renderer.observe(statebuffer=statebuffer)

    print(agent1.id)

    thread_agent1 = threading.Thread(target=agent_thread, args=(agent1,))
    thread_agent2 = threading.Thread(target=agent_thread, args=(agent2,))
    #thread_agent3 = threading.Thread(target=agent_thread, args=(agent3,))
    #thread_agent4 = threading.Thread(target=agent_thread, args=(agent4,))

    thread_renderer = threading.Thread(target=render_thread, args=(renderer,))

    thread_renderer.start()
    thread_agent1.start()
    thread_agent2.start()
    #thread_agent3.start()
    #thread_agent4.start()

    thread_agent1.join()
    thread_agent2.join()
    #thread_agent3.join()
    #thread_agent4.join()
    thread_renderer.join()

    #agent.print_state()